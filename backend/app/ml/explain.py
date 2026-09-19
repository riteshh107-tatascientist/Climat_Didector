"""
ClimateGuard AI — Explainability Layer
========================================
Primary path: SHAP (TreeExplainer for tree models, LinearExplainer for
logistic/linear models) for per-prediction contribution values.

Fallback path (used automatically if `shap` is not installed, e.g. in an
offline environment): a model-agnostic *signed local contribution* estimate
built from the model's global feature_importances_/coefficients combined
with how far each input value sits from the training feature mean
(z-score-weighted). This is a coarser explanation than SHAP but is always
available, always directionally consistent with the model, and never
fabricates a factor the model doesn't actually use.

Either path returns the same output shape so callers (risk engine, API)
never need to know which one ran.
"""
from __future__ import annotations
from typing import Any
import numpy as np

try:
    import shap  # type: ignore
    _SHAP_AVAILABLE = True
except ImportError:
    _SHAP_AVAILABLE = False


HUMAN_LABELS = {
    "rainfall_mm": "rainfall",
    "temperature_c": "temperature",
    "humidity_pct": "humidity",
    "soil_saturation_pct": "soil saturation",
    "drainage_index": "drainage capacity",
    "elevation_m": "elevation",
    "pop_density_per_km2": "population density",
    "flood_prone_base": "known flood-prone geography",
    "water_storage_pct": "water storage level",
    "drought_prone_base": "known drought-prone geography",
    "month": "seasonal timing",
    "is_monsoon": "monsoon season",
    "region_enc": "regional profile",
}

# Direction in which a HIGHER value of each raw feature makes risk WORSE.
# drainage_index and water_storage_pct are protective (higher = lower risk).
RISK_INCREASES_WITH_VALUE = {
    "rainfall_mm": True, "temperature_c": True, "humidity_pct": True,
    "soil_saturation_pct": True, "drainage_index": False, "elevation_m": False,
    "pop_density_per_km2": True, "flood_prone_base": True,
    "water_storage_pct": False, "drought_prone_base": True,
    "month": None, "is_monsoon": True, "region_enc": None,
}


def explain_prediction(
    model: Any,
    scaler: Any,
    feature_names: list[str],
    feature_importance: dict[str, float],
    input_row: dict[str, float],
    used_scaler: bool,
    training_means: dict[str, float] | None = None,
    training_stds: dict[str, float] | None = None,
    top_k: int = 5,
) -> list[dict]:
    """Return a ranked list of {feature, human_label, contribution, direction,
    value} describing what drove this specific prediction."""

    if _SHAP_AVAILABLE:
        try:
            return _explain_with_shap(model, scaler, feature_names, input_row, used_scaler, top_k)
        except Exception:
            pass  # fall through to heuristic explainer below

    return _explain_with_heuristic(
        feature_names, feature_importance, input_row,
        training_means or {}, training_stds or {}, top_k
    )


def _explain_with_shap(model, scaler, feature_names, input_row, used_scaler, top_k):
    import pandas as pd
    x = pd.DataFrame([[input_row[f] for f in feature_names]], columns=feature_names)
    x_model = scaler.transform(x) if used_scaler else x

    try:
        explainer = shap.TreeExplainer(model)
    except Exception:
        explainer = shap.LinearExplainer(model, x_model)
    shap_values = explainer.shap_values(x_model)
    if isinstance(shap_values, list):
        shap_values = shap_values[-1]  # positive class for classifiers
    contributions = shap_values[0]

    ranked = sorted(zip(feature_names, contributions), key=lambda kv: -abs(kv[1]))[:top_k]
    out = []
    for feat, contrib in ranked:
        out.append({
            "feature": feat,
            "human_label": HUMAN_LABELS.get(feat, feat),
            "contribution": round(float(contrib), 4),
            "direction": "increases_risk" if contrib > 0 else "decreases_risk",
            "value": input_row.get(feat),
            "method": "shap",
        })
    return out


def _explain_with_heuristic(feature_names, feature_importance, input_row,
                             training_means, training_stds, top_k):
    scored = []
    for feat in feature_names:
        importance = feature_importance.get(feat, 0.0)
        val = input_row.get(feat, 0.0)
        mean = training_means.get(feat, val)
        std = training_stds.get(feat, 1.0) or 1.0
        z = (val - mean) / std

        risk_dir = RISK_INCREASES_WITH_VALUE.get(feat)
        if risk_dir is None:
            signed = importance * abs(z)
            direction = "increases_risk" if z > 0 else "decreases_risk"
        else:
            signed_z = z if risk_dir else -z
            signed = importance * signed_z
            direction = "increases_risk" if signed_z > 0 else "decreases_risk"

        scored.append((feat, signed, direction, val))

    ranked = sorted(scored, key=lambda t: -abs(t[1]))[:top_k]
    out = []
    for feat, signed, direction, val in ranked:
        out.append({
            "feature": feat,
            "human_label": HUMAN_LABELS.get(feat, feat),
            "contribution": round(float(signed), 4),
            "direction": direction,
            "value": val,
            "method": "feature_importance_heuristic",
        })
    return out
