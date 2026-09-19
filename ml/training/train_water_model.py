"""Train the Water Stress classifier (same pattern as flood model)."""
from __future__ import annotations
import os, sys, json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from ml.preprocessing.features import add_temporal_features, encode_categoricals, WATER_FEATURES

BASE = os.path.join(os.path.dirname(__file__), "..", "..")
DATA_PATH = os.path.join(BASE, "data", "datasets", "water_stress.csv")
MODEL_DIR = os.path.join(BASE, "ml", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def main():
    df = pd.read_csv(DATA_PATH)
    df = add_temporal_features(df)
    df, encoders = encode_categoricals(df, ["region"])

    X = df[WATER_FEATURES]
    y = df["water_stress_event"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=12, min_samples_leaf=5,
            class_weight="balanced", random_state=42, n_jobs=-1
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=3, learning_rate=0.08, random_state=42
        ),
    }

    results, fitted = {}, {}
    for name, model in candidates.items():
        if name == "logistic_regression":
            model.fit(X_train_s, y_train)
            proba = model.predict_proba(X_test_s)[:, 1]
            preds = model.predict(X_test_s)
        else:
            model.fit(X_train, y_train)
            proba = model.predict_proba(X_test)[:, 1]
            preds = model.predict(X_test)
        fitted[name] = model
        results[name] = {
            "accuracy": round(accuracy_score(y_test, preds), 4),
            "precision": round(precision_score(y_test, preds), 4),
            "recall": round(recall_score(y_test, preds), 4),
            "f1_score": round(f1_score(y_test, preds), 4),
            "roc_auc": round(roc_auc_score(y_test, proba), 4),
            "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
        }

    best_name = max(results, key=lambda k: results[k]["roc_auc"])
    best_model = fitted[best_name]
    print("Water stress model comparison:")
    for name, m in results.items():
        print(f"  {name:20s} AUC={m['roc_auc']:.4f} F1={m['f1_score']:.4f} "
              f"Precision={m['precision']:.4f} Recall={m['recall']:.4f}")
    print(f"Selected best model: {best_name}")

    if hasattr(best_model, "feature_importances_"):
        importances = dict(zip(WATER_FEATURES, best_model.feature_importances_.tolist()))
    else:
        importances = dict(zip(WATER_FEATURES, np.abs(best_model.coef_[0]).tolist()))
    importances = dict(sorted(importances.items(), key=lambda kv: -kv[1]))

    joblib.dump(best_model, os.path.join(MODEL_DIR, "water_model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "water_scaler.joblib"))
    with open(os.path.join(MODEL_DIR, "water_encoders.json"), "w") as f:
        json.dump(encoders, f, indent=2)
    with open(os.path.join(MODEL_DIR, "water_metrics.json"), "w") as f:
        json.dump({
            "best_model": best_name,
            "used_scaler": best_name == "logistic_regression",
            "features": WATER_FEATURES,
            "all_model_results": results,
            "feature_importance": importances,
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "feature_means": {c: float(X_train[c].mean()) for c in WATER_FEATURES},
            "feature_stds": {c: float(X_train[c].std()) for c in WATER_FEATURES},
        }, f, indent=2)
    print("Saved model, scaler, encoders, metrics to", MODEL_DIR)


if __name__ == "__main__":
    main()
