import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.core.risk_engine import (
    score_to_level, classification_confidence, regression_confidence, build_assessment
)


class TestRiskEngine(unittest.TestCase):
    def test_score_to_level_boundaries(self):
        self.assertEqual(score_to_level(0), "LOW")
        self.assertEqual(score_to_level(24.9), "LOW")
        self.assertEqual(score_to_level(25), "MODERATE")
        self.assertEqual(score_to_level(49.9), "MODERATE")
        self.assertEqual(score_to_level(50), "HIGH")
        self.assertEqual(score_to_level(74.9), "HIGH")
        self.assertEqual(score_to_level(75), "CRITICAL")
        self.assertEqual(score_to_level(100), "CRITICAL")

    def test_classification_confidence_at_boundary_is_zero(self):
        self.assertEqual(classification_confidence(0.5), 0.0)

    def test_classification_confidence_at_extremes_is_high(self):
        self.assertEqual(classification_confidence(1.0), 100.0)
        self.assertEqual(classification_confidence(0.0), 100.0)

    def test_regression_confidence_zero_std_is_safe(self):
        conf = regression_confidence(10, 10, 0)
        self.assertEqual(conf, 50.0)  # must not divide by zero

    def test_build_assessment_classification(self):
        a = build_assessment(
            module="flood", probability_or_value=0.9, is_classification=True,
            key_factors=[], model_version="flood_v1_test",
        )
        self.assertEqual(a.risk_score, 90.0)
        self.assertEqual(a.risk_level, "CRITICAL")

    def test_build_assessment_regression_clips_at_100(self):
        a = build_assessment(
            module="agriculture", probability_or_value=80, is_classification=False,
            key_factors=[], model_version="agri_v1_test",
            train_mean=25, train_std=6, regression_scale=2.0,
        )
        self.assertEqual(a.risk_score, 100.0)


if __name__ == "__main__":
    unittest.main()
