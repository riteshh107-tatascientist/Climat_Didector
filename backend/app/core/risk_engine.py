"""
ClimateGuard AI — Unified Risk Engine
========================================
Converts a raw model output (probability or regression value) plus its
explanation into a standardized, documented risk object used by every
module (flood, water, agriculture, city, waste, energy).

Scoring logic (kept intentionally transparent, not a black box):

    risk_score (0-100) = calibrated_probability * 100        [classification]
                        = min(100, regression_value * scale)  [regression]

    risk_level:
        0  - 24   -> LOW
        25 - 49   -> MODERATE
        50 - 74   -> HIGH
        75 - 100  -> CRITICAL

    confidence: derived from how far the model's probability/prediction is
    from the training-set decision boundary / spread — a prediction near
    0.5 (classification) or near the training mean (regression) is treated
    as lower-confidence than one far in either direction.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import math

RISK_THRESHOLDS = [
    (0, 25, "LOW"),
    (25, 50, "MODERATE"),
    (50, 75, "HIGH"),
    (75, 101, "CRITICAL"),
]


@dataclass
class RiskAssessment:
    module: str
    risk_score: float
    risk_level: str
    confidence: float
    key_factors: list[dict]
    raw_output: float
    model_version: str
    estimated_impact: Optional[str] = None


def score_to_level(score: float) -> str:
    for low, high, label in RISK_THRESHOLDS:
        if low <= score < high:
            return label
    return "CRITICAL"


def classification_confidence(probability: float) -> float:
    """Distance from decision boundary (0.5), scaled to 0-100.
    A probability of 0.5 -> 0% confidence in the class call, near 0 or 1
    approaches 100%."""
    return round(min(100.0, abs(probability - 0.5) * 200), 1)


def regression_confidence(value: float, train_mean: float, train_std: float) -> float:
    """How many standard deviations the prediction sits from the training
    mean, compressed into a 0-100 confidence-in-signal proxy. This measures
    how 'unusual/decisive' the reading is, not literal statistical
    confidence — documented here to avoid overclaiming precision."""
    if train_std <= 0:
        return 50.0
    z = abs(value - train_mean) / train_std
    return round(min(100.0, 40 + z * 20), 1)


def build_assessment(
    module: str,
    probability_or_value: float,
    is_classification: bool,
    key_factors: list[dict],
    model_version: str,
    train_mean: float | None = None,
    train_std: float | None = None,
    regression_scale: float = 1.0,
    estimated_impact: Optional[str] = None,
) -> RiskAssessment:
    if is_classification:
        score = round(probability_or_value * 100, 1)
        confidence = classification_confidence(probability_or_value)
    else:
        score = round(min(100.0, probability_or_value * regression_scale), 1)
        confidence = regression_confidence(
            probability_or_value, train_mean or 0.0, train_std or 1.0
        )

    level = score_to_level(score)
    return RiskAssessment(
        module=module,
        risk_score=score,
        risk_level=level,
        confidence=confidence,
        key_factors=key_factors,
        raw_output=round(float(probability_or_value), 4),
        model_version=model_version,
        estimated_impact=estimated_impact,
    )


def assessment_to_dict(a: RiskAssessment) -> dict:
    return {
        "module": a.module,
        "risk_score": a.risk_score,
        "risk_level": a.risk_level,
        "confidence": a.confidence,
        "key_factors": a.key_factors,
        "raw_model_output": a.raw_output,
        "model_version": a.model_version,
        "estimated_impact": a.estimated_impact,
    }
