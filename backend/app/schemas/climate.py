"""Pydantic v2 schemas for API request validation and response shaping."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class FloodRiskRequest(BaseModel):
    region: str = Field(..., examples=["Mumbai"])
    rainfall_mm: float = Field(..., ge=0, le=1000)
    temperature_c: float = Field(..., ge=-10, le=55)
    humidity_pct: float = Field(..., ge=0, le=100)
    soil_saturation_pct: float = Field(..., ge=0, le=100)
    drainage_index: float = Field(..., ge=0, le=100)
    elevation_m: float = Field(..., ge=0, le=9000)
    pop_density_per_km2: float = Field(..., ge=0)
    flood_prone_base: int = Field(0, ge=0, le=1)
    month: int = Field(..., ge=1, le=12)
    is_monsoon: int = Field(0, ge=0, le=1)


class WaterRiskRequest(BaseModel):
    region: str
    rainfall_mm: float = Field(..., ge=0, le=1000)
    temperature_c: float = Field(..., ge=-10, le=55)
    humidity_pct: float = Field(..., ge=0, le=100)
    water_storage_pct: float = Field(..., ge=0, le=100)
    pop_density_per_km2: float = Field(..., ge=0)
    drought_prone_base: int = Field(0, ge=0, le=1)
    month: int = Field(..., ge=1, le=12)
    is_monsoon: int = Field(0, ge=0, le=1)


class AgricultureRequest(BaseModel):
    region: str
    rainfall_mm: float = Field(..., ge=0, le=1000)
    temperature_c: float = Field(..., ge=-10, le=55)
    humidity_pct: float = Field(..., ge=0, le=100)
    soil_saturation_pct: float = Field(..., ge=0, le=100)
    drought_prone_base: int = Field(0, ge=0, le=1)
    month: int = Field(..., ge=1, le=12)
    is_monsoon: int = Field(0, ge=0, le=1)


class WasteRequest(BaseModel):
    region: str
    organic_pct: float = Field(..., ge=0, le=100)
    recyclable_pct: float = Field(..., ge=0, le=100)
    collection_efficiency_pct: float = Field(..., ge=0, le=100)


class EnergyRequest(BaseModel):
    region: str
    energy_demand_mwh: float = Field(..., ge=0)
    carbon_emissions_tco2: float = Field(..., ge=0)
    avg_temp_c: float = Field(..., ge=-10, le=55)


class KeyFactor(BaseModel):
    feature: str
    human_label: str
    contribution: float
    direction: str
    value: Optional[float] = None
    method: str


class Recommendation(BaseModel):
    problem: str
    reason: str
    action: str
    expected_benefit: str
    driven_by_factor: Optional[str] = None


class RiskResponse(BaseModel):
    module: str
    risk_score: float
    risk_level: str
    confidence: float
    key_factors: list[KeyFactor]
    raw_model_output: float
    model_version: str
    estimated_impact: Optional[str] = None
    recommendations: list[Recommendation]
