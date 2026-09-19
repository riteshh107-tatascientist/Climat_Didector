"""Train the Agriculture crop-stress regression model."""
from __future__ import annotations
import os, sys, json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from ml.preprocessing.features import add_temporal_features, encode_categoricals, AGRI_FEATURES

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
DATA_PATH = os.path.join(BASE, "data", "datasets", "agriculture_stress.csv")
MODEL_DIR = os.path.join(BASE, "ml", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def main():
    df = pd.read_csv(DATA_PATH)
    df = add_temporal_features(df)
    df, encoders = encode_categoricals(df, ["region"])

    X = df[AGRI_FEATURES]
    y = df["crop_stress_index"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    candidates = {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(
            n_estimators=300, max_depth=12, min_samples_leaf=5, random_state=42, n_jobs=-1
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=200, max_depth=3, learning_rate=0.08, random_state=42
        ),
    }

    results, fitted = {}, {}
    for name, model in candidates.items():
        if name == "linear_regression":
            model.fit(X_train_s, y_train)
            preds = model.predict(X_test_s)
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
        fitted[name] = model
        mse = mean_squared_error(y_test, preds)
        results[name] = {
            "mae": round(mean_absolute_error(y_test, preds), 4),
            "rmse": round(float(np.sqrt(mse)), 4),
            "r2_score": round(r2_score(y_test, preds), 4),
        }

    best_name = min(results, key=lambda k: results[k]["rmse"])
    best_model = fitted[best_name]
    print("Agriculture crop-stress model comparison:")
    for name, m in results.items():
        print(f"  {name:20s} RMSE={m['rmse']:.4f} MAE={m['mae']:.4f} R2={m['r2_score']:.4f}")
    print(f"Selected best model: {best_name}")

    if hasattr(best_model, "feature_importances_"):
        importances = dict(zip(AGRI_FEATURES, best_model.feature_importances_.tolist()))
    else:
        importances = dict(zip(AGRI_FEATURES, np.abs(best_model.coef_).tolist()))
    importances = dict(sorted(importances.items(), key=lambda kv: -kv[1]))

    joblib.dump(best_model, os.path.join(MODEL_DIR, "agriculture_model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "agriculture_scaler.joblib"))
    with open(os.path.join(MODEL_DIR, "agriculture_encoders.json"), "w") as f:
        json.dump(encoders, f, indent=2)
    with open(os.path.join(MODEL_DIR, "agriculture_metrics.json"), "w") as f:
        json.dump({
            "best_model": best_name,
            "used_scaler": best_name == "linear_regression",
            "features": AGRI_FEATURES,
            "all_model_results": results,
            "feature_importance": importances,
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "feature_means": {c: float(X_train[c].mean()) for c in AGRI_FEATURES},
            "feature_stds": {c: float(X_train[c].std()) for c in AGRI_FEATURES},
        }, f, indent=2)
    print("Saved model, scaler, encoders, metrics to", MODEL_DIR)


if __name__ == "__main__":
    main()
