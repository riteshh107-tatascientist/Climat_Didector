"""
ClimateGuard AI — Dataset Generation Module
=============================================

DATA SOURCE NOTE (read this first)
-----------------------------------
This module is the single ingestion boundary for all raw data used by
ClimateGuard AI. In a fully networked deployment, `fetch_*` functions below
would call live/public sources directly:

    - IMD (India Meteorological Department) Gridded Rainfall & station data
    - NASA POWER API (solar/meteorological, agriculture-grade)
    - NOAA Climate Data Online
    - ISRO Bhuvan / public remote sensing layers
    - data.gov.in (Open Government Data Platform India)
    - World Bank Climate Change Knowledge Portal

The sandbox this project was authored in has NO outbound network access
(pip installs and HTTP requests both fail — verified during development).
Because of that, this module ships with a `synthetic` provider that
generates data statistically anchored to publicly documented facts about
Indian climate (examples: IMD long-period-average monsoon rainfall ~880mm
national average with regional variation from ~150mm in western Rajasthan
to >3000mm in parts of the Northeast; Indian district temperatures ranging
roughly 5-48°C seasonally; typical Indian district populations; standard
NRDWP/CPCB waste-generation benchmarks of ~0.3-0.6 kg/capita/day, etc.)
rather than inventing arbitrary numbers.

This is explicitly flagged as a LIMITATION in README.md. The provider
interface (`DataProvider`) is designed so swapping `SyntheticProvider` for
a `LiveAPIProvider` (real IMD/NASA/data.gov.in calls) requires no change to
downstream preprocessing, training, or serving code — only a different
class satisfying the same contract.

Run:
    python generate_datasets.py
writes CSVs into ../../data/datasets/
"""

from __future__ import annotations

import os
import json
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional

RNG_SEED = 42
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "datasets")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Reference tables: real, publicly-known Indian district/region climate
# characteristics used to anchor the synthetic generator (not invented).
# Values are approximate long-period averages compiled from IMD/Census
# public summaries and are used only to shape realistic distributions.
# ---------------------------------------------------------------------------
INDIA_REGIONS = pd.DataFrame([
    # region,           state,             avg_annual_rainfall_mm, avg_temp_c, flood_prone, drought_prone, pop_density_class
    ("Kochi",            "Kerala",          3000, 27.5, 1, 0, "high"),
    ("Mumbai",           "Maharashtra",     2200, 27.0, 1, 0, "very_high"),
    ("Guwahati",         "Assam",           1800, 24.5, 1, 0, "medium"),
    ("Kolkata",          "West Bengal",     1600, 26.8, 1, 0, "very_high"),
    ("Patna",            "Bihar",           1100, 26.0, 1, 0, "high"),
    ("Chennai",          "Tamil Nadu",      1400, 28.5, 1, 0, "very_high"),
    ("Bhubaneswar",      "Odisha",          1500, 27.0, 1, 0, "medium"),
    ("Lucknow",          "Uttar Pradesh",   1000, 26.5, 1, 0, "high"),
    ("Ahmedabad",        "Gujarat",         800,  27.5, 0, 1, "very_high"),
    ("Jaipur",           "Rajasthan",       550,  26.0, 0, 1, "medium"),
    ("Bikaner",          "Rajasthan",       260,  27.0, 0, 1, "low"),
    ("Nagpur",           "Maharashtra",     1100, 27.5, 0, 1, "medium"),
    ("Pune",             "Maharashtra",     750,  24.5, 0, 1, "high"),
    ("Bengaluru",        "Karnataka",       900,  23.5, 0, 1, "very_high"),
    ("Hyderabad",        "Telangana",       800,  26.5, 0, 1, "very_high"),
    ("Indore",           "Madhya Pradesh",  950,  25.5, 0, 1, "medium"),
    ("Bhopal",           "Madhya Pradesh",  1150, 25.0, 0, 0, "medium"),
    ("Chandigarh",       "Punjab",          1000, 24.0, 0, 0, "medium"),
    ("Amritsar",         "Punjab",          650,  24.5, 0, 1, "medium"),
    ("Dehradun",         "Uttarakhand",     2000, 21.0, 1, 0, "low"),
    ("Shimla",           "Himachal Pradesh",1500, 15.0, 1, 0, "low"),
    ("Srinagar",         "Jammu & Kashmir", 700,  13.0, 1, 0, "low"),
    ("Ranchi",           "Jharkhand",       1400, 24.0, 0, 1, "medium"),
    ("Raipur",           "Chhattisgarh",    1300, 26.0, 0, 1, "medium"),
    ("Thiruvananthapuram","Kerala",         1800, 27.5, 1, 0, "high"),
    ("Visakhapatnam",    "Andhra Pradesh",  1100, 28.0, 1, 0, "medium"),
    ("Surat",            "Gujarat",         1200, 27.0, 1, 0, "very_high"),
    ("Varanasi",         "Uttar Pradesh",   1050, 26.0, 1, 0, "high"),
    ("Agra",             "Uttar Pradesh",   700,  26.5, 0, 1, "high"),
    ("Jodhpur",          "Rajasthan",       360,  27.0, 0, 1, "low"),
], columns=["region", "state", "avg_annual_rainfall_mm", "avg_temp_c",
            "flood_prone_base", "drought_prone_base", "pop_density_class"])

DENSITY_MAP = {"low": 150, "medium": 800, "high": 3500, "very_high": 9000}


class DataProvider:
    """Abstract ingestion contract. Swap SyntheticProvider for a real one."""

    def get_regions(self) -> pd.DataFrame:
        raise NotImplementedError

    def get_daily_weather(self, n_days: int) -> pd.DataFrame:
        raise NotImplementedError


class SyntheticProvider(DataProvider):
    """
    Statistically-anchored synthetic data generator.
    See module docstring for why this exists and what it is anchored to.
    """

    def __init__(self, seed: int = RNG_SEED):
        self.rng = np.random.default_rng(seed)

    def get_regions(self) -> pd.DataFrame:
        return INDIA_REGIONS.copy()

    def get_daily_weather(self, n_days: int = 1000) -> pd.DataFrame:
        rows = []
        regions = INDIA_REGIONS
        dates = pd.date_range("2019-01-01", periods=n_days, freq="D")
        for _, reg in regions.iterrows():
            month_factor = np.array([
                0.3, 0.2, 0.25, 0.35, 0.55, 1.6, 2.4, 2.2, 1.4, 0.55, 0.25, 0.25
            ])  # Indian monsoon seasonality (Jun-Sep peak)
            for d in dates:
                mf = month_factor[d.month - 1]
                base_daily_mm = (reg["avg_annual_rainfall_mm"] / 365.0) * mf
                rainfall = max(0.0, self.rng.gamma(shape=0.6, scale=max(base_daily_mm, 0.5)))
                temp_seasonal = 4 * np.sin((d.dayofyear / 365.0) * 2 * np.pi - 1.4)
                temperature = reg["avg_temp_c"] + temp_seasonal + self.rng.normal(0, 1.5)
                humidity = np.clip(40 + mf * 15 + self.rng.normal(0, 8), 15, 99)
                soil_saturation = np.clip(
                    30 + rainfall * 0.8 + self.rng.normal(0, 10), 5, 100
                )
                drainage_index = np.clip(
                    self.rng.normal(
                        60 if reg["pop_density_class"] in ("high", "very_high") else 75, 15
                    ), 10, 100
                )  # lower in dense urban areas -> more waterlogging risk
                elevation_m = max(5, self.rng.normal(
                    250 if reg["region"] not in ("Shimla", "Dehradun", "Srinagar") else 1800, 300
                ))
                water_storage_pct = np.clip(self.rng.normal(55, 20), 2, 100)
                rows.append(dict(
                    date=d, region=reg["region"], state=reg["state"],
                    rainfall_mm=round(rainfall, 2),
                    temperature_c=round(temperature, 2),
                    humidity_pct=round(humidity, 2),
                    soil_saturation_pct=round(soil_saturation, 2),
                    drainage_index=round(drainage_index, 2),
                    elevation_m=round(elevation_m, 1),
                    water_storage_pct=round(water_storage_pct, 2),
                    pop_density_per_km2=DENSITY_MAP[reg["pop_density_class"]] * (
                        1 + self.rng.normal(0, 0.1)
                    ),
                    flood_prone_base=reg["flood_prone_base"],
                    drought_prone_base=reg["drought_prone_base"],
                ))
        return pd.DataFrame(rows)


def _label_flood_risk(row) -> int:
    """Physically-motivated heuristic label used as ground truth for training.
    High rainfall + saturated soil + poor drainage + flood-prone geography
    => flood event more likely. This mirrors how hydrology risk indices
    (e.g., simplified CN/runoff-based indicators) combine these factors."""
    score = (
        0.035 * row.rainfall_mm +
        0.02 * row.soil_saturation_pct +
        0.02 * (100 - row.drainage_index) +
        8 * row.flood_prone_base +
        0.0015 * row.pop_density_per_km2 -
        0.01 * row.elevation_m
    )
    prob = 1 / (1 + np.exp(-(score - 12) / 6))
    return int(np.random.default_rng(abs(hash(str(row.date) + row.region)) % (2**32)).random() < prob)


def _label_water_stress(row) -> int:
    score = (
        -0.03 * row.water_storage_pct +
        -0.015 * row.rainfall_mm +
        0.02 * row.temperature_c +
        6 * row.drought_prone_base +
        0.001 * row.pop_density_per_km2
    )
    prob = 1 / (1 + np.exp(-(score - 1) / 3))
    return int(np.random.default_rng(abs(hash("w" + str(row.date) + row.region)) % (2**32)).random() < prob)


def build_flood_dataset(weather: pd.DataFrame) -> pd.DataFrame:
    df = weather.copy()
    df["flood_event"] = df.apply(_label_flood_risk, axis=1)
    cols = ["date", "region", "state", "rainfall_mm", "temperature_c", "humidity_pct",
            "soil_saturation_pct", "drainage_index", "elevation_m", "pop_density_per_km2",
            "flood_prone_base", "flood_event"]
    return df[cols]


def build_water_dataset(weather: pd.DataFrame) -> pd.DataFrame:
    df = weather.copy()
    df["water_stress_event"] = df.apply(_label_water_stress, axis=1)
    cols = ["date", "region", "state", "rainfall_mm", "temperature_c", "humidity_pct",
            "water_storage_pct", "pop_density_per_km2", "drought_prone_base",
            "water_stress_event"]
    return df[cols]


def build_agriculture_dataset(weather: pd.DataFrame) -> pd.DataFrame:
    """Crop yield risk regression target (0-100 stress index) derived from
    heat stress, water deficit and humidity — standard agronomic drivers."""
    df = weather.copy()
    rng = np.random.default_rng(RNG_SEED + 1)
    heat_stress = np.clip((df.temperature_c - 30) * 4, 0, None)
    water_deficit = np.clip(40 - df.rainfall_mm, 0, None) * 0.5
    humidity_penalty = np.clip(df.humidity_pct - 85, 0, None) * 0.3
    noise = rng.normal(0, 5, size=len(df))
    crop_stress_index = np.clip(heat_stress + water_deficit + humidity_penalty + noise, 0, 100)
    df["crop_stress_index"] = np.round(crop_stress_index, 2)
    cols = ["date", "region", "state", "rainfall_mm", "temperature_c", "humidity_pct",
            "soil_saturation_pct", "drought_prone_base", "crop_stress_index"]
    return df[cols]


def build_waste_dataset(regions: pd.DataFrame) -> pd.DataFrame:
    """District-level waste composition, anchored to CPCB benchmark ranges
    (~0.3-0.6 kg/capita/day; organic fraction 50-60% typical Indian MSW)."""
    rng = np.random.default_rng(RNG_SEED + 2)
    rows = []
    for _, reg in regions.iterrows():
        pop = DENSITY_MAP[reg["pop_density_class"]] * rng.uniform(8, 40)  # approx district pop proxy
        per_capita_kg = np.clip(rng.normal(0.45, 0.08), 0.25, 0.7)
        organic_pct = np.clip(rng.normal(55, 8), 30, 75)
        recyclable_pct = np.clip(rng.normal(20, 6), 5, 40)
        collection_efficiency = np.clip(rng.normal(
            70 if reg["pop_density_class"] in ("high", "very_high") else 50, 15), 20, 98)
        rows.append(dict(
            region=reg["region"], state=reg["state"],
            population_est=int(pop),
            waste_generated_tpd=round(pop * per_capita_kg / 1000, 2),
            organic_pct=round(organic_pct, 2),
            recyclable_pct=round(recyclable_pct, 2),
            collection_efficiency_pct=round(collection_efficiency, 2),
        ))
    return pd.DataFrame(rows)


def build_energy_dataset(regions: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """Monthly per-region energy demand & implied carbon intensity, anchored
    to CEA-published India grid emission factor (~0.71-0.82 tCO2/MWh range
    depending on year; we use 0.75 as a representative constant)."""
    rng = np.random.default_rng(RNG_SEED + 3)
    GRID_EMISSION_FACTOR = 0.75  # tCO2 per MWh, representative of CEA CO2 baseline database
    monthly = weather.copy()
    monthly["month"] = monthly.date.dt.to_period("M")
    agg = monthly.groupby(["region", "state", "month"]).agg(
        avg_temp_c=("temperature_c", "mean"),
        avg_humidity=("humidity_pct", "mean"),
        pop_density_per_km2=("pop_density_per_km2", "mean"),
    ).reset_index()
    cooling_demand = np.clip(agg.avg_temp_c - 24, 0, None) ** 1.3
    heating_demand = np.clip(18 - agg.avg_temp_c, 0, None) ** 1.1
    base_load = agg.pop_density_per_km2 * 0.002
    energy_mwh = base_load + cooling_demand * 3 + heating_demand * 1.5 + rng.normal(0, 2, len(agg))
    energy_mwh = np.clip(energy_mwh, 1, None)
    agg["energy_demand_mwh"] = round(energy_mwh, 2)
    agg["carbon_emissions_tco2"] = round(energy_mwh * GRID_EMISSION_FACTOR, 2)
    agg["month"] = agg["month"].astype(str)
    return agg


def main():
    provider = SyntheticProvider()
    regions = provider.get_regions()
    weather = provider.get_daily_weather(n_days=730)  # 2 years daily, 30 regions

    flood_df = build_flood_dataset(weather)
    water_df = build_water_dataset(weather)
    agri_df = build_agriculture_dataset(weather)
    waste_df = build_waste_dataset(regions)
    energy_df = build_energy_dataset(regions, weather)

    flood_df.to_csv(os.path.join(OUT_DIR, "flood_risk.csv"), index=False)
    water_df.to_csv(os.path.join(OUT_DIR, "water_stress.csv"), index=False)
    agri_df.to_csv(os.path.join(OUT_DIR, "agriculture_stress.csv"), index=False)
    waste_df.to_csv(os.path.join(OUT_DIR, "waste_circular_economy.csv"), index=False)
    energy_df.to_csv(os.path.join(OUT_DIR, "energy_carbon.csv"), index=False)
    regions.to_csv(os.path.join(OUT_DIR, "regions_reference.csv"), index=False)

    manifest = {
        "generated_by": "ml/data/generate_datasets.py",
        "provider": "SyntheticProvider (anchored to public IMD/CPCB/CEA reference ranges)",
        "note": "No live network access was available in the build environment; "
                "see module docstring / README Limitations for the real-data swap plan.",
        "files": {
            "flood_risk.csv": {"rows": len(flood_df), "target": "flood_event (binary)"},
            "water_stress.csv": {"rows": len(water_df), "target": "water_stress_event (binary)"},
            "agriculture_stress.csv": {"rows": len(agri_df), "target": "crop_stress_index (0-100 regression)"},
            "waste_circular_economy.csv": {"rows": len(waste_df), "target": "none (descriptive/rules-based)"},
            "energy_carbon.csv": {"rows": len(energy_df), "target": "energy_demand_mwh / carbon_emissions_tco2 (regression)"},
        },
    }
    with open(os.path.join(OUT_DIR, "MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print("Datasets written to", os.path.abspath(OUT_DIR))
    for k, v in manifest["files"].items():
        print(f"  {k}: {v['rows']} rows -> target: {v['target']}")


if __name__ == "__main__":
    main()
