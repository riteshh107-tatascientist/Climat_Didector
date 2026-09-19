"""
ClimateGuard AI — Prediction Service
=======================================
Loads trained models once (at process start) and exposes a clean
`predict_*` function per module. This is the only place that talks to
joblib files directly — API routes call into here, never load a model
themselves.
"""
from __future__ import annotations
import os
import json
import joblib
from functools import lru_cache

from app.core.risk_engine import build_assessment, assessment_to_dict
from app.core.recommendation_engine import generate_recommendations
from app.ml.explain import explain_prediction

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")


class LoadedModel:
    def __init__(self, name: str):
        self.name = name
        self.model = joblib.load(os.path.join(MODEL_DIR, f"{name}_model.joblib"))
        self.scaler = joblib.load(os.path.join(MODEL_DIR, f"{name}_scaler.joblib"))
        with open(os.path.join(MODEL_DIR, f"{name}_encoders.json")) as f:
            self.encoders = json.load(f)
        with open(os.path.join(MODEL_DIR, f"{name}_metrics.json")) as f:
            self.metrics = json.load(f)
        self.features = self.metrics["features"]
        self.used_scaler = self.metrics["used_scaler"]
        self.feature_importance = self.metrics["feature_importance"]
        self.feature_means = self.metrics.get("feature_means", {})
        self.feature_stds = self.metrics.get("feature_stds", {})
        self.version = f"{name}_v1_{self.metrics['best_model']}"

    def encode_region(self, region: str) -> int:
        mapping = self.encoders.get("region", {})
        if region in mapping:
            return mapping[region]
        return max(mapping.values(), default=0) + 1  # unseen-region fallback bucket

    def prepare_row(self, raw: dict) -> dict:
        row = dict(raw)
        row["region_enc"] = self.encode_region(raw.get("region", ""))
        return {f: row.get(f, 0.0) for f in self.features}

    def predict_proba(self, row: dict) -> float:
        import pandas as pd
        x = pd.DataFrame([[row[f] for f in self.features]], columns=self.features)
        x_model = self.scaler.transform(x) if self.used_scaler else x
        if hasattr(self.model, "predict_proba"):
            return float(self.model.predict_proba(x_model)[0][1])
        return float(self.model.predict(x_model)[0])


@lru_cache(maxsize=None)
def get_model(name: str) -> LoadedModel:
    return LoadedModel(name)


def _run_classification(module: str, input_features: dict) -> dict:
    lm = get_model(module)
    row = lm.prepare_row(input_features)
    probability = lm.predict_proba(row)

    key_factors = explain_prediction(
        model=lm.model, scaler=lm.scaler, feature_names=lm.features,
        feature_importance=lm.feature_importance, input_row=row,
        used_scaler=lm.used_scaler, training_means=lm.feature_means,
        training_stds=lm.feature_stds, top_k=5,
    )
    assessment = build_assessment(
        module=module, probability_or_value=probability, is_classification=True,
        key_factors=key_factors, model_version=lm.version,
    )
    recommendations = generate_recommendations(module, key_factors)
    result = assessment_to_dict(assessment)
    result["recommendations"] = recommendations
    result["input"] = input_features
    return result


def predict_flood_risk(input_features: dict) -> dict:
    return _run_classification("flood", input_features)


def predict_water_risk(input_features: dict) -> dict:
    return _run_classification("water", input_features)


def predict_agriculture_stress(input_features: dict) -> dict:
    lm = get_model("agriculture")
    row = lm.prepare_row(input_features)
    value = lm.predict_proba(row)  # for regressors this calls .predict via predict_proba fallback

    key_factors = explain_prediction(
        model=lm.model, scaler=lm.scaler, feature_names=lm.features,
        feature_importance=lm.feature_importance, input_row=row,
        used_scaler=lm.used_scaler, training_means=lm.feature_means,
        training_stds=lm.feature_stds, top_k=5,
    )
    train_mean = sum(lm.feature_means.values()) / max(len(lm.feature_means), 1)
    assessment = build_assessment(
        module="agriculture", probability_or_value=value, is_classification=False,
        key_factors=key_factors, model_version=lm.version,
        train_mean=25.0, train_std=6.0, regression_scale=2.0,
        estimated_impact=f"Crop stress index {value:.1f}/100 — higher values indicate "
                          f"greater expected yield pressure this cycle.",
    )
    recommendations = generate_recommendations("agriculture", key_factors)
    result = assessment_to_dict(assessment)
    result["recommendations"] = recommendations
    result["input"] = input_features
    result["crop_stress_index"] = round(value, 2)
    return result


def preload_all_models() -> dict:
    """Called at API startup so first request isn't slow and so a broken
    artifact fails fast and loudly instead of on the first user request."""
    status = {}
    for name in ("flood", "water", "agriculture"):
        try:
            lm = get_model(name)
            status[name] = {"loaded": True, "version": lm.version}
        except Exception as e:
            status[name] = {"loaded": False, "error": str(e)}
    return status
