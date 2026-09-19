"""
Dashboard API — every number here comes from a real SQL aggregation over
the predictions/risk_assessments tables. Nothing is hardcoded; a fresh
database returns honest zeros/empty lists rather than fake placeholder
numbers (see get_overview's explicit empty-state handling).
"""
from __future__ import annotations
from collections import Counter
import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.db import get_db
from app.models.orm import Prediction, RiskAssessmentORM, Location, EnvironmentalObservation
from app.api.deps import get_current_user_optional

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", summary="Top-level dashboard statistics")
def overview(db: Session = Depends(get_db), current_user=Depends(get_current_user_optional)):
    q = db.query(Prediction, RiskAssessmentORM).join(
        RiskAssessmentORM, RiskAssessmentORM.prediction_id == Prediction.id
    )
    if current_user is not None:
        q = q.filter(Prediction.user_id == current_user.id)
    rows = q.all()

    total = len(rows)
    if total == 0:
        return {
            "total_assessments": 0, "high_risk_assessments": 0,
            "average_risk_score": None, "modules_covered": [],
            "note": "No assessments yet — run a prediction to populate the dashboard.",
        }

    high_risk = sum(1 for _, ra in rows if ra.risk_level in ("HIGH", "CRITICAL"))
    avg_score = round(sum(ra.risk_score for _, ra in rows) / total, 2)
    modules = sorted({p.module for p, _ in rows})

    return {
        "total_assessments": total,
        "high_risk_assessments": high_risk,
        "average_risk_score": avg_score,
        "modules_covered": modules,
    }


@router.get("/risk-distribution", summary="Count of assessments per risk level")
def risk_distribution(db: Session = Depends(get_db), current_user=Depends(get_current_user_optional)):
    q = db.query(RiskAssessmentORM.risk_level, func.count(RiskAssessmentORM.id))
    if current_user is not None:
        q = q.join(Prediction, Prediction.id == RiskAssessmentORM.prediction_id).filter(
            Prediction.user_id == current_user.id
        )
    rows = q.group_by(RiskAssessmentORM.risk_level).all()
    dist = {level: 0 for level in ("LOW", "MODERATE", "HIGH", "CRITICAL")}
    for level, count in rows:
        dist[level] = count
    return dist


@router.get("/recent", summary="Most recent risk assessments")
def recent_assessments(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db),
                        current_user=Depends(get_current_user_optional)):
    q = db.query(Prediction, RiskAssessmentORM, Location).join(
        RiskAssessmentORM, RiskAssessmentORM.prediction_id == Prediction.id
    ).join(Location, Location.id == Prediction.location_id)
    if current_user is not None:
        q = q.filter(Prediction.user_id == current_user.id)
    rows = q.order_by(Prediction.predicted_at.desc()).limit(limit).all()

    return [
        {
            "prediction_id": p.id, "module": p.module, "region": loc.region, "state": loc.state,
            "risk_score": ra.risk_score, "risk_level": ra.risk_level, "confidence": ra.confidence,
            "predicted_at": p.predicted_at.isoformat() if p.predicted_at else None,
        }
        for p, ra, loc in rows
    ]


@router.get("/top-risk-factors", summary="Most frequently contributing risk factors across assessments")
def top_risk_factors(module: str | None = None, limit: int = Query(5, ge=1, le=20),
                      db: Session = Depends(get_db), current_user=Depends(get_current_user_optional)):
    q = db.query(RiskAssessmentORM, Prediction).join(
        Prediction, Prediction.id == RiskAssessmentORM.prediction_id
    )
    if module:
        q = q.filter(Prediction.module == module)
    if current_user is not None:
        q = q.filter(Prediction.user_id == current_user.id)
    rows = q.all()

    counter = Counter()
    for ra, _ in rows:
        try:
            factors = json.loads(ra.key_factors_json)
        except (TypeError, json.JSONDecodeError):
            continue
        for f in factors:
            if f.get("direction") == "increases_risk":
                counter[f.get("human_label", f.get("feature"))] += 1

    return [{"factor": label, "occurrences": count} for label, count in counter.most_common(limit)]


@router.get("/environmental-trends", summary="Average environmental readings over time for a region")
def environmental_trends(region: str, db: Session = Depends(get_db)):
    loc = db.query(Location).filter(Location.region == region).first()
    if not loc:
        return {"region": region, "trend": [], "note": "No observations recorded for this region yet."}

    rows = (
        db.query(EnvironmentalObservation)
        .filter(EnvironmentalObservation.location_id == loc.id)
        .order_by(EnvironmentalObservation.observed_at.asc())
        .all()
    )
    return {
        "region": region,
        "trend": [
            {
                "observed_at": r.observed_at.isoformat() if r.observed_at else None,
                "rainfall_mm": r.rainfall_mm, "temperature_c": r.temperature_c,
                "humidity_pct": r.humidity_pct,
            }
            for r in rows
        ],
    }


@router.get("/location-comparison", summary="Compare latest risk scores across locations")
def location_comparison(module: str, db: Session = Depends(get_db)):
    subq = (
        db.query(
            Prediction.location_id,
            func.max(Prediction.predicted_at).label("latest"),
        )
        .filter(Prediction.module == module)
        .group_by(Prediction.location_id)
        .subquery()
    )
    rows = (
        db.query(Location, RiskAssessmentORM)
        .join(Prediction, Prediction.location_id == Location.id)
        .join(RiskAssessmentORM, RiskAssessmentORM.prediction_id == Prediction.id)
        .join(subq, (Prediction.location_id == subq.c.location_id) & (Prediction.predicted_at == subq.c.latest))
        .filter(Prediction.module == module)
        .all()
    )
    return [
        {"region": loc.region, "state": loc.state, "risk_score": ra.risk_score, "risk_level": ra.risk_level}
        for loc, ra in rows
    ]
