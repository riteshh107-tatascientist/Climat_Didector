import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.core.recommendation_engine import (
    generate_recommendations, waste_recommendation, energy_recommendation
)


class TestRecommendationEngine(unittest.TestCase):
    def test_flood_recommendation_driven_by_rainfall(self):
        key_factors = [
            {"feature": "rainfall_mm", "human_label": "rainfall",
             "direction": "increases_risk", "contribution": 1.2, "value": 200},
        ]
        recs = generate_recommendations("flood", key_factors)
        self.assertEqual(len(recs), 1)
        self.assertIn("rainfall", recs[0]["driven_by_factor"])
        for key in ("problem", "reason", "action", "expected_benefit"):
            self.assertTrue(recs[0][key])

    def test_recommendation_ignores_protective_factors(self):
        key_factors = [
            {"feature": "drainage_index", "human_label": "drainage capacity",
             "direction": "decreases_risk", "contribution": -0.8, "value": 90},
        ]
        recs = generate_recommendations("flood", key_factors)
        # No factor increases risk -> falls back to the "no dominant factor" message
        self.assertEqual(recs[0]["driven_by_factor"], None)

    def test_waste_recommendation_flags_low_collection(self):
        recs = waste_recommendation(organic_pct=40, recyclable_pct=10, collection_efficiency_pct=45)
        problems = [r["problem"] for r in recs]
        self.assertTrue(any("Collection efficiency" in p for p in problems))

    def test_energy_recommendation_flags_heat(self):
        recs = energy_recommendation(energy_demand_mwh=100, carbon_emissions_tco2=50, avg_temp_c=35)
        problems = [r["problem"] for r in recs]
        self.assertTrue(any("Cooling" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
