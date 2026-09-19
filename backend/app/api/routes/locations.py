from __future__ import annotations
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.db import get_db
from app.models.orm import Location, Prediction, RiskAssessmentORM

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", summary="Search/list known locations")
def list_locations(q: str | None = Query(None, description="Search by region or state name"),
                    db: Session = Depends(get_db)):
    query = db.query(Location)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Location.region.ilike(like), Location.state.ilike(like)))
    locations = query.order_by(Location.region.asc()).limit(50).all()
    return [
        {"id": l.id, "region": l.region, "state": l.state, "flood_prone": bool(l.flood_prone_base),
         "drought_prone": bool(l.drought_prone_base)}
        for l in locations
    ]


@router.get("/{region}/intelligence", summary="Latest risk snapshot for a specific location, per module")
def location_intelligence(region: str, db: Session = Depends(get_db)):
    location = db.query(Location).filter(Location.region == region).first()
    if not location:
        raise HTTPException(status_code=404, detail=f"No data found for location '{region}'. "
                                                       f"Run a prediction for this region first.")

    modules_seen = (
        db.query(Prediction.module).filter(Prediction.location_id == location.id).distinct().all()
    )
    snapshot = {}
    for (module,) in modules_seen:
        latest = (
            db.query(Prediction, RiskAssessmentORM)
            .join(RiskAssessmentORM, RiskAssessmentORM.prediction_id == Prediction.id)
            .filter(Prediction.location_id == location.id, Prediction.module == module)
            .order_by(Prediction.predicted_at.desc())
            .first()
        )
        if latest:
            p, ra = latest
            snapshot[module] = {
                "risk_score": ra.risk_score, "risk_level": ra.risk_level,
                "confidence": ra.confidence, "key_factors": json.loads(ra.key_factors_json),
                "predicted_at": p.predicted_at.isoformat() if p.predicted_at else None,
            }

    return {
        "region": location.region, "state": location.state,
        "flood_prone": bool(location.flood_prone_base),
        "drought_prone": bool(location.drought_prone_base),
        "modules": snapshot,
    }
