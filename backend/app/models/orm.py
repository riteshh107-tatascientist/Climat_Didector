"""
ClimateGuard AI — SQLAlchemy ORM Models
===========================================
Mirrors backend/app/models/schema.sql exactly (that file is validated
against SQLite in the test suite; this is the ORM layer the FastAPI app
uses at runtime against SQLite locally or PostgreSQL in production via
DATABASE_URL).
"""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, TIMESTAMP, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    organization = Column(String)
    role = Column(String, default="viewer")
    is_active = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    region = Column(String, nullable=False)
    state = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    elevation_m = Column(Float)
    pop_density_per_km2 = Column(Float)
    flood_prone_base = Column(Integer, default=0)
    drought_prone_base = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("region", "state"),)


class EnvironmentalObservation(Base):
    __tablename__ = "environmental_observations"
    id = Column(Integer, primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    observed_at = Column(TIMESTAMP, nullable=False)
    rainfall_mm = Column(Float)
    temperature_c = Column(Float)
    humidity_pct = Column(Float)
    soil_saturation_pct = Column(Float)
    drainage_index = Column(Float)
    water_storage_pct = Column(Float)
    source = Column(String, default="synthetic_v1")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    location = relationship("Location")


class ModelVersion(Base):
    __tablename__ = "model_versions"
    id = Column(Integer, primary_key=True)
    module = Column(String, nullable=False)
    version_label = Column(String, nullable=False)
    algorithm = Column(String, nullable=False)
    metrics_json = Column(Text, nullable=False)
    trained_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_active = Column(Integer, default=1)
    __table_args__ = (UniqueConstraint("module", "version_label"),)


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    module = Column(String, nullable=False)
    model_version_id = Column(Integer, ForeignKey("model_versions.id"))
    input_features_json = Column(Text, nullable=False)
    raw_output = Column(Float, nullable=False)
    predicted_at = Column(TIMESTAMP, default=datetime.utcnow)
    risk_assessment = relationship("RiskAssessmentORM", uselist=False, back_populates="prediction")


class RiskAssessmentORM(Base):
    __tablename__ = "risk_assessments"
    id = Column(Integer, primary_key=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    key_factors_json = Column(Text, nullable=False)
    estimated_impact = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    prediction = relationship("Prediction", back_populates="risk_assessment")
    recommendations = relationship("RecommendationORM", back_populates="risk_assessment")


class RecommendationORM(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True)
    risk_assessment_id = Column(Integer, ForeignKey("risk_assessments.id"), nullable=False)
    problem = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    expected_benefit = Column(Text, nullable=False)
    driven_by_factor = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    risk_assessment = relationship("RiskAssessmentORM", back_populates="recommendations")
