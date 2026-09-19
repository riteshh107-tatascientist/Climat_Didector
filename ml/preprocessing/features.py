"""
ClimateGuard AI — Feature Engineering
======================================
Shared preprocessing used by all training scripts AND by the live
prediction service, so train/serve feature logic never drifts apart.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def add_temporal_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["month"] = df[date_col].dt.month
    df["day_of_year"] = df[date_col].dt.dayofyear
    df["is_monsoon"] = df["month"].isin([6, 7, 8, 9]).astype(int)
    return df


def encode_categoricals(df: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, dict]:
    """Simple, deterministic label encoding (fit dict must be saved and
    reused at inference — see ml/models/*_encoders.json)."""
    df = df.copy()
    encoders = {}
    for c in cols:
        if c not in df.columns:
            continue
        cats = sorted(df[c].astype(str).unique().tolist())
        mapping = {cat: i for i, cat in enumerate(cats)}
        df[c + "_enc"] = df[c].astype(str).map(mapping)
        encoders[c] = mapping
    return df, encoders


def apply_encoders(df: pd.DataFrame, encoders: dict) -> pd.DataFrame:
    df = df.copy()
    for c, mapping in encoders.items():
        if c not in df.columns:
            continue
        unknown = max(mapping.values()) + 1 if mapping else 0
        df[c + "_enc"] = df[c].astype(str).map(mapping).fillna(unknown)
    return df


FLOOD_FEATURES = [
    "rainfall_mm", "temperature_c", "humidity_pct", "soil_saturation_pct",
    "drainage_index", "elevation_m", "pop_density_per_km2", "flood_prone_base",
    "month", "is_monsoon", "region_enc",
]

WATER_FEATURES = [
    "rainfall_mm", "temperature_c", "humidity_pct", "water_storage_pct",
    "pop_density_per_km2", "drought_prone_base", "month", "is_monsoon", "region_enc",
]

AGRI_FEATURES = [
    "rainfall_mm", "temperature_c", "humidity_pct", "soil_saturation_pct",
    "drought_prone_base", "month", "is_monsoon", "region_enc",
]
