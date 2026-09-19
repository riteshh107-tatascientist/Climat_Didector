"""API routes for the three ML-backed modules (Phase 1): flood, water,
agriculture. Waste and energy expose rules-based endpoints (no ML model
in Phase 1 — see README "Phase 2" section). Phase 2 adds: auth-aware
logging (predictions are attributed to the logged-in user when present,
anonymous/demo otherwise), prediction history/detail lookup, and a single
unified POST /predict endpoint that dispatches by `module`."""
from __future__ import annotations
import json
from typing import Literal, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.schemas.climate import (
    FloodRiskRequest, WaterRiskRequest, AgricultureRequest,
    WasteRequest, EnergyRequest, RiskResponse,
)
from app.ml.predictors import (
    predict_flood_risk, predict_water_risk, predict_agriculture_stress, get_model,
)
from app.core.recommendation_engine import waste_recommendation, energy_recommendation
from app.models.db import get_db
from app.models.orm import Prediction, RiskAssessmentORM, Location
from app.services.persistence import log_prediction
from app.api.deps import get_current_user_optional

router = APIRouter()

MODULE_HANDLERS = {
    "flood": (predict_flood_risk, FloodRiskRequest),
    "water": (predict_water_risk, WaterRiskRequest),
    "agriculture": (predict_agriculture_stress, AgricultureRequest),
}


def _predict_and_log(module: str, payload_dict: dict, db: Session, current_user) -> dict:
    handler, _ = MODULE_HANDLERS[module]
    try:
        result = handler(payload_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{module} prediction failed: {e}")
    try:
        lm = get_model(module)
        log_prediction(
            db, module, payload_dict["region"], payload_dict, result,
            algorithm=lm.metrics["best_model"], metrics=lm.metrics["all_model_results"],
            user_id=current_user.id if current_user else None,
        )
    except Exception:
        # Logging failure must never take down a successful prediction —
        # the caller still gets their risk assessment even if the DB write fails.
        db.rollback()
    return result


class UnifiedPredictRequest(BaseModel):
    module: Literal["flood", "water", "agriculture"]
    region: str
    rainfall_mm: Optional[float] = None
    temperature_c: Optional[float] = None
    humidity_pct: Optional[float] = None
    soil_saturation_pct: Optional[float] = None
    drainage_index: Optional[float] = None
    elevation_m: Optional[float] = None
    pop_density_per_km2: Optional[float] = None
    flood_prone_base: Optional[int] = 0
    water_storage_pct: Optional[float] = None
    drought_prone_base: Optional[int] = 0
    month: int
    is_monsoon: Optional[int] = 0


@router.post("/predict", response_model=RiskResponse, tags=["climate-intelligence"],
             summary="Unified prediction endpoint — dispatches to the model named by `module`")
def unified_predict(payload: UnifiedPredictRequest, db: Session = Depends(get_db),
                     current_user=Depends(get_current_user_optional)):
    _, schema_cls = MODULE_HANDLERS[payload.module]
    try:
        validated = schema_cls(**payload.model_dump(exclude={"module"}, exclude_none=True))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid parameters for module '{payload.module}': {e}")
    return _predict_and_log(payload.module, validated.model_dump(), db, current_user)


@router.post("/flood/predict", response_model=RiskResponse, tags=["flood"])
def predict_flood(payload: FloodRiskRequest, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user_optional)):
    return _predict_and_log("flood", payload.model_dump(), db, current_user)


@router.post("/water/predict", response_model=RiskResponse, tags=["water"])
def predict_water(payload: WaterRiskRequest, db: Session = Depends(get_db),
                   current_user=Depends(get_current_user_optional)):
    return _predict_and_log("water", payload.model_dump(), db, current_user)


@router.post("/agriculture/predict", response_model=RiskResponse, tags=["agriculture"])
def predict_agriculture(payload: AgricultureRequest, db: Session = Depends(get_db),
                         current_user=Depends(get_current_user_optional)):
    return _predict_and_log("agriculture", payload.model_dump(), db, current_user)


@router.get("/predictions/history", tags=["climate-intelligence"],
            summary="Paginated prediction history, optionally filtered by module/region")
def prediction_history(
    module: Optional[str] = None, region: Optional[str] = None,
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), current_user=Depends(get_current_user_optional),
):
    q = db.query(Prediction, RiskAssessmentORM, Location).join(
        RiskAssessmentORM, RiskAssessmentORM.prediction_id == Prediction.id
    ).join(Location, Location.id == Prediction.location_id)
    if current_user is not None:
        q = q.filter(Prediction.user_id == current_user.id)
    if module:
        q = q.filter(Prediction.module == module)
    if region:
        q = q.filter(Location.region == region)

    total = q.count()
    rows = (
        q.order_by(Prediction.predicted_at.desc())
        .offset((page - 1) * page_size).limit(page_size).all()
    )
    return {
        "total": total, "page": page, "page_size": page_size,
        "results": [
            {
                "prediction_id": p.id, "module": p.module, "region": loc.region, "state": loc.state,
                "risk_score": ra.risk_score, "risk_level": ra.risk_level, "confidence": ra.confidence,
                "model_version": p.model_version_id, "predicted_at": p.predicted_at.isoformat() if p.predicted_at else None,
            }
            for p, ra, loc in rows
        ],
    }


@router.get("/predictions/{prediction_id}", tags=["climate-intelligence"],
            summary="Full detail for one prediction: inputs, score, factors, recommendations")
def prediction_detail(prediction_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(Prediction, RiskAssessmentORM, Location)
        .join(RiskAssessmentORM, RiskAssessmentORM.prediction_id == Prediction.id)
        .join(Location, Location.id == Prediction.location_id)
        .filter(Prediction.id == prediction_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail=f"Prediction {prediction_id} not found")
    p, ra, loc = row
    recommendations = [
        {
            "problem": r.problem, "reason": r.reason, "action": r.action,
            "expected_benefit": r.expected_benefit, "driven_by_factor": r.driven_by_factor,
        }
        for r in ra.recommendations
    ]
    return {
        "prediction_id": p.id, "module": p.module, "region": loc.region, "state": loc.state,
        "input_features": json.loads(p.input_features_json),
        "risk_score": ra.risk_score, "risk_level": ra.risk_level, "confidence": ra.confidence,
        "key_factors": json.loads(ra.key_factors_json), "estimated_impact": ra.estimated_impact,
        "recommendations": recommendations,
        "predicted_at": p.predicted_at.isoformat() if p.predicted_at else None,
    }


@router.post("/waste/recommend", tags=["waste"])
def recommend_waste(payload: WasteRequest):
    recs = waste_recommendation(
        payload.organic_pct, payload.recyclable_pct, payload.collection_efficiency_pct
    )
    return {"module": "waste", "region": payload.region, "recommendations": recs}


@router.post("/energy/recommend", tags=["energy"])
def recommend_energy(payload: EnergyRequest):
    recs = energy_recommendation(
        payload.energy_demand_mwh, payload.carbon_emissions_tco2, payload.avg_temp_c
    )
    return {"module": "energy", "region": payload.region, "recommendations": recs}
