import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.ml.predictors import (
    predict_flood_risk, predict_water_risk, predict_agriculture_stress, preload_all_models
)

VALID_LEVELS = {"LOW", "MODERATE", "HIGH", "CRITICAL"}


class TestPredictors(unittest.TestCase):
    def test_models_load(self):
        status = preload_all_models()
        for module, info in status.items():
            self.assertTrue(info["loaded"], f"{module} failed to load: {info}")

    def test_flood_high_risk_input(self):
        result = predict_flood_risk({
            "region": "Mumbai", "rainfall_mm": 220.0, "temperature_c": 28.0, "humidity_pct": 90.0,
            "soil_saturation_pct": 90.0, "drainage_index": 25.0, "elevation_m": 8.0,
            "pop_density_per_km2": 9500.0, "flood_prone_base": 1, "month": 7, "is_monsoon": 1,
        })
        self.assertIn(result["risk_level"], VALID_LEVELS)
        self.assertGreaterEqual(result["risk_score"], 0)
        self.assertLessEqual(result["risk_score"], 100)
        self.assertGreaterEqual(len(result["key_factors"]), 1)
        self.assertGreaterEqual(len(result["recommendations"]), 1)
        # heavy rain + saturated soil + poor drainage should score as elevated risk
        self.assertGreater(result["risk_score"], 50)

    def test_flood_low_risk_input(self):
        result = predict_flood_risk({
            "region": "Jodhpur", "rainfall_mm": 2.0, "temperature_c": 30.0, "humidity_pct": 25.0,
            "soil_saturation_pct": 10.0, "drainage_index": 85.0, "elevation_m": 230.0,
            "pop_density_per_km2": 150.0, "flood_prone_base": 0, "month": 4, "is_monsoon": 0,
        })
        self.assertLess(result["risk_score"], 50)

    def test_water_prediction_shape(self):
        result = predict_water_risk({
            "region": "Jaipur", "rainfall_mm": 5.0, "temperature_c": 38.0, "humidity_pct": 20.0,
            "water_storage_pct": 15.0, "pop_density_per_km2": 800.0, "drought_prone_base": 1,
            "month": 5, "is_monsoon": 0,
        })
        self.assertIn(result["risk_level"], VALID_LEVELS)
        self.assertIn("recommendations", result)

    def test_agriculture_prediction_shape(self):
        result = predict_agriculture_stress({
            "region": "Nagpur", "rainfall_mm": 3.0, "temperature_c": 41.0, "humidity_pct": 30.0,
            "soil_saturation_pct": 15.0, "drought_prone_base": 1, "month": 5, "is_monsoon": 0,
        })
        self.assertIn("crop_stress_index", result)
        self.assertGreaterEqual(result["crop_stress_index"], 0)

    def test_unseen_region_does_not_crash(self):
        result = predict_flood_risk({
            "region": "SomeNewTownNotInTrainingData", "rainfall_mm": 50.0, "temperature_c": 27.0,
            "humidity_pct": 60.0, "soil_saturation_pct": 40.0, "drainage_index": 60.0,
            "elevation_m": 100.0, "pop_density_per_km2": 500.0, "flood_prone_base": 0,
            "month": 6, "is_monsoon": 1,
        })
        self.assertIn(result["risk_level"], VALID_LEVELS)


if __name__ == "__main__":
    unittest.main()
