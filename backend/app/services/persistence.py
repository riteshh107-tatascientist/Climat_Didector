"""Persists every prediction + risk assessment + its recommendations so
each prediction is fully traceable later (input, model version, output,
explanation, and what was recommended)."""
from __future__ import annotations
import json
from sqlalchemy.orm import Session
from app.models.orm import (
    Location, ModelVersion, Prediction, RiskAssessmentORM, RecommendationORM
)


def get_or_create_location(db: Session, region: str, state: str = "unknown", **extra) -> Location:
    loc = db.query(Location).filter_by(region=region, state=state).first()
    if loc:
        return loc
    loc = Location(region=region, state=state, **extra)
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


def get_or_create_model_version(db: Session, module: str, version_label: str,
                                 algorithm: str, metrics: dict) -> ModelVersion:
    mv = db.query(ModelVersion).filter_by(module=module, version_label=version_label).first()
    if mv:
        return mv
    mv = ModelVersion(module=module, version_label=version_label, algorithm=algorithm,
                       metrics_json=json.dumps(metrics))
    db.add(mv)
    db.commit()
    db.refresh(mv)
    return mv


def log_prediction(db: Session, module: str, region: str, input_features: dict,
                    result: dict, algorithm: str, metrics: dict, user_id: int | None = None) -> int:
    location = get_or_create_location(db, region=region, state=input_features.get("state", "unknown"))
    model_version = get_or_create_model_version(
        db, module=module, version_label=result["model_version"], algorithm=algorithm, metrics=metrics
    )
    prediction = Prediction(
        user_id=user_id, location_id=location.id, module=module,
        model_version_id=model_version.id,
        input_features_json=json.dumps(input_features),
        raw_output=result["raw_model_output"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    assessment = RiskAssessmentORM(
        prediction_id=prediction.id, risk_score=result["risk_score"],
        risk_level=result["risk_level"], confidence=result["confidence"],
        key_factors_json=json.dumps(result["key_factors"]),
        estimated_impact=result.get("estimated_impact"),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    for rec in result.get("recommendations", []):
        db.add(RecommendationORM(
            risk_assessment_id=assessment.id, problem=rec["problem"], reason=rec["reason"],
            action=rec["action"], expected_benefit=rec["expected_benefit"],
            driven_by_factor=rec.get("driven_by_factor"),
        ))
    db.commit()
    return prediction.id
