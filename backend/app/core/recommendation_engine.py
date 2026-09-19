"""
ClimateGuard AI — Recommendation Engine
===========================================
Produces structured recommendations (problem / reason / action / expected
benefit) that are derived from the actual key_factors returned by the risk
engine for a specific prediction — never generic boilerplate independent of
the input. Each module has a small rule table keyed by which factors are
currently pushing risk up; the top contributing factor(s) select which
rule(s) fire.
"""
from __future__ import annotations
from typing import List, Dict

# Each rule: trigger feature -> (problem, reason_template, action, benefit)
FLOOD_RULES = {
    "rainfall_mm": (
        "Elevated rainfall is the dominant risk driver",
        "Rainfall levels are running high relative to what this area's drainage system is built for.",
        "Activate flood-preparedness protocols: clear stormwater drains, pre-position pumps, "
        "and issue an early advisory to low-lying wards.",
        "Reduces waterlogging duration and property damage during peak rainfall.",
    ),
    "soil_saturation_pct": (
        "Soil is already near saturation",
        "High soil moisture means additional rainfall runs off rather than infiltrating, "
        "increasing surface flood risk.",
        "Prioritize surface-runoff management (desilting drains, temporary check-dams) "
        "over infiltration-based mitigation for the next rain event.",
        "Cuts peak runoff volume during the next rainfall event.",
    ),
    "drainage_index": (
        "Drainage capacity is a limiting factor",
        "This area's drainage index is below what current rainfall patterns require.",
        "Prioritize drain desilting and capacity upgrades in this ward/region ahead of monsoon.",
        "Directly increases the volume of water the area can safely move away.",
    ),
    "flood_prone_base": (
        "Location has a known flood-prone geography",
        "Historical and geographic indicators mark this region as structurally flood-prone.",
        "Maintain this location in the priority-monitoring tier and pre-stage emergency response resources.",
        "Shortens emergency response time when conditions deteriorate.",
    ),
    "pop_density_per_km2": (
        "High population density amplifies flood impact",
        "Dense populations increase both exposure and evacuation complexity if flooding occurs.",
        "Establish or verify evacuation routes and shelter capacity for this density level.",
        "Reduces casualties/displacement impact if a flood event occurs.",
    ),
}

WATER_RULES = {
    "water_storage_pct": (
        "Water storage reserves are low",
        "Current storage levels are below what's needed to buffer against continued low rainfall.",
        "Prioritize rainwater harvesting structures and audit/reduce non-revenue water (leakage) losses.",
        "Extends how long existing storage can meet demand before shortage.",
    ),
    "rainfall_mm": (
        "Rainfall deficit is contributing to water stress",
        "Recent rainfall is below the level needed to naturally replenish local water sources.",
        "Activate demand-management measures (tiered water pricing/rationing schedule) "
        "and monitor groundwater levels weekly.",
        "Slows depletion of remaining water reserves.",
    ),
    "temperature_c": (
        "High temperatures are increasing water demand and evaporation loss",
        "Elevated temperatures raise both consumption and evaporative losses from open reservoirs.",
        "Cover/shade open storage where feasible and shift non-essential water use to cooler hours.",
        "Reduces evaporative loss and smooths peak demand.",
    ),
    "drought_prone_base": (
        "Location has a known drought-prone profile",
        "Historical drought-proneness means this region has less resilience buffer than average.",
        "Fast-track drought-contingency plans (tanker allocation, priority supply zones).",
        "Reduces response lag if conditions continue to worsen.",
    ),
}

AGRI_RULES = {
    "temperature_c": (
        "Heat stress is elevated for current crop stage",
        "Temperatures are pushing into a range associated with crop heat stress.",
        "Advise farmers to shift irrigation to early morning/evening and consider heat-tolerant "
        "variety planning for the next sowing cycle.",
        "Reduces yield loss from heat-induced stress.",
    ),
    "rainfall_mm": (
        "Rainfall is insufficient for current crop water demand",
        "Rainfall in the area is below what standing crops typically need at this stage.",
        "Recommend supplemental irrigation scheduling and mulching to retain soil moisture.",
        "Reduces water-deficit-driven yield loss.",
    ),
    "humidity_pct": (
        "High humidity raises fungal/pest disease risk",
        "Sustained high humidity creates favorable conditions for fungal pathogens and pest pressure.",
        "Recommend preventive fungicide scheduling and increased field monitoring frequency.",
        "Lowers probability of a disease outbreak reducing yield.",
    ),
    "drought_prone_base": (
        "Region has underlying drought susceptibility",
        "This area's baseline drought-proneness compounds current conditions.",
        "Prioritize drought-resilient crop varieties and water-efficient irrigation (drip/sprinkler) investment.",
        "Builds structural resilience against recurring seasonal stress.",
    ),
}

RULES_BY_MODULE = {
    "flood": FLOOD_RULES,
    "water": WATER_RULES,
    "agriculture": AGRI_RULES,
}


def generate_recommendations(module: str, key_factors: List[Dict], max_recs: int = 3) -> List[Dict]:
    """key_factors: output of explain_prediction() — ranked, signed contributions.
    Only factors that are actually *increasing* risk generate action
    recommendations (a factor decreasing risk doesn't need an intervention)."""
    rules = RULES_BY_MODULE.get(module, {})
    recs = []
    for factor in key_factors:
        if factor["direction"] != "increases_risk":
            continue
        rule = rules.get(factor["feature"])
        if not rule:
            continue
        problem, reason, action, benefit = rule
        recs.append({
            "problem": problem,
            "reason": reason,
            "action": action,
            "expected_benefit": benefit,
            "driven_by_factor": factor["human_label"],
        })
        if len(recs) >= max_recs:
            break

    if not recs:
        recs.append({
            "problem": "No single factor dominates current risk",
            "reason": "Conditions are within a range where no individual driver strongly elevates risk.",
            "action": "Continue routine monitoring; no immediate intervention required.",
            "expected_benefit": "Maintains preparedness without over-allocating resources.",
            "driven_by_factor": None,
        })
    return recs


# --- Rules-based modules that don't have ML classifiers in Phase 1 ---

def waste_recommendation(organic_pct: float, recyclable_pct: float,
                          collection_efficiency_pct: float) -> List[Dict]:
    recs = []
    if organic_pct >= 50:
        recs.append({
            "problem": "High organic waste fraction",
            "reason": f"Organic waste is {organic_pct:.0f}% of the stream, well above the "
                      f"threshold where composting/biogas becomes economically viable.",
            "action": "Establish decentralized composting or biogas units at the ward level.",
            "expected_benefit": "Cuts landfill volume and generates usable compost/energy.",
        })
    if recyclable_pct >= 20:
        recs.append({
            "problem": "Meaningful recyclable fraction is going unrecovered",
            "reason": f"Recyclables make up {recyclable_pct:.0f}% of waste generated.",
            "action": "Introduce/expand source-segregation and a material recovery facility (MRF).",
            "expected_benefit": "Increases material recovery revenue and reduces landfill burden.",
        })
    if collection_efficiency_pct < 60:
        recs.append({
            "problem": "Collection efficiency is below a functional threshold",
            "reason": f"Only {collection_efficiency_pct:.0f}% of generated waste is being collected.",
            "action": "Expand collection routes/frequency and add community collection points.",
            "expected_benefit": "Reduces uncollected waste accumulation and associated health risk.",
        })
    if not recs:
        recs.append({
            "problem": "Waste system parameters are within acceptable ranges",
            "reason": "No single metric is critically off-target.",
            "action": "Maintain current collection and processing cadence.",
            "expected_benefit": "Sustains current performance level.",
        })
    return recs


def energy_recommendation(energy_demand_mwh: float, carbon_emissions_tco2: float,
                           avg_temp_c: float) -> List[Dict]:
    recs = []
    if avg_temp_c >= 30:
        recs.append({
            "problem": "Cooling-driven demand spike",
            "reason": f"Average temperature of {avg_temp_c:.1f}°C is pushing cooling-related "
                      f"electricity demand higher.",
            "action": "Promote efficient-cooling incentives (star-rated ACs, reflective roofing) "
                      "and consider demand-response programs for peak hours.",
            "expected_benefit": "Flattens peak demand and reduces grid strain during heat events.",
        })
    if carbon_emissions_tco2 / max(energy_demand_mwh, 1) > 0.7:
        recs.append({
            "problem": "Carbon intensity of supplied energy is high",
            "reason": "Emissions per unit of energy delivered indicate a grid mix weighted toward "
                      "fossil generation.",
            "action": "Prioritize rooftop solar and renewable procurement for this region's load.",
            "expected_benefit": "Reduces carbon emissions per unit of energy consumed.",
        })
    if not recs:
        recs.append({
            "problem": "Energy/carbon profile is within a manageable range",
            "reason": "No single driver is critically elevated.",
            "action": "Continue monitoring; maintain existing efficiency programs.",
            "expected_benefit": "Sustains current performance level.",
        })
    return recs
