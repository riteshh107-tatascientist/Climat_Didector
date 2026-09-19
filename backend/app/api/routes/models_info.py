from __future__ import annotations
from fastapi import APIRouter, HTTPException
from app.ml.predictors import get_model

router = APIRouter(prefix="/models", tags=["models"])

VALID_MODULES = ("flood", "water", "agriculture")


@router.get("", summary="List available model modules and their active version")
def list_models():
    out = []
    for name in VALID_MODULES:
        try:
            lm = get_model(name)
            out.append({"module": name, "version": lm.version, "algorithm": lm.metrics["best_model"]})
        except Exception as e:
            out.append({"module": name, "error": str(e)})
    return out


@router.get("/{module}/performance", summary="Full evaluation metrics for a model module")
def model_performance(module: str):
    if module not in VALID_MODULES:
        raise HTTPException(status_code=404, detail=f"Unknown module '{module}'. Valid: {VALID_MODULES}")
    lm = get_model(module)
    return {
        "module": module,
        "version": lm.version,
        "selected_algorithm": lm.metrics["best_model"],
        "all_candidate_results": lm.metrics["all_model_results"],
        "feature_importance": lm.metrics["feature_importance"],
        "train_rows": lm.metrics["train_rows"],
        "test_rows": lm.metrics["test_rows"],
    }
