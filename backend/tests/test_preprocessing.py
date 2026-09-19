import os, sys, unittest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from ml.preprocessing.features import add_temporal_features, encode_categoricals, apply_encoders


class TestPreprocessing(unittest.TestCase):
    def test_temporal_features(self):
        df = pd.DataFrame({"date": ["2024-07-15", "2024-01-01"]})
        out = add_temporal_features(df)
        self.assertEqual(out.loc[0, "month"], 7)
        self.assertEqual(out.loc[0, "is_monsoon"], 1)
        self.assertEqual(out.loc[1, "is_monsoon"], 0)

    def test_encode_categoricals_roundtrip(self):
        df = pd.DataFrame({"region": ["Mumbai", "Pune", "Mumbai"]})
        encoded, encoders = encode_categoricals(df, ["region"])
        self.assertIn("region_enc", encoded.columns)
        self.assertEqual(encoded.loc[0, "region_enc"], encoded.loc[2, "region_enc"])
        self.assertIn("Mumbai", encoders["region"])

    def test_apply_encoders_handles_unseen(self):
        df = pd.DataFrame({"region": ["Mumbai", "Pune"]})
        _, encoders = encode_categoricals(df, ["region"])
        new_df = pd.DataFrame({"region": ["Chennai"]})  # unseen at fit time
        result = apply_encoders(new_df, encoders)
        self.assertFalse(result["region_enc"].isnull().any())


if __name__ == "__main__":
    unittest.main()
