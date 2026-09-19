"""Requires fastapi/sqlalchemy/httpx — see conftest.py docstring."""
import pytest

VALID_FLOOD_PAYLOAD = {
    "region": "Mumbai", "rainfall_mm": 180.0, "temperature_c": 28.0, "humidity_pct": 88.0,
    "soil_saturation_pct": 85.0, "drainage_index": 35.0, "elevation_m": 12.0,
    "pop_density_per_km2": 9000.0, "flood_prone_base": 1, "month": 7, "is_monsoon": 1,
}


class TestFloodPrediction:
    def test_predict_returns_full_shape(self, client):
        resp = client.post("/api/v1/flood/predict", json=VALID_FLOOD_PAYLOAD)
        assert resp.status_code == 200
        body = resp.json()
        for key in ("risk_score", "risk_level", "confidence", "key_factors",
                    "recommendations", "model_version"):
            assert key in body
        assert body["risk_level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")

    def test_predict_missing_field_returns_422_not_500(self, client):
        bad_payload = dict(VALID_FLOOD_PAYLOAD)
        del bad_payload["rainfall_mm"]
        resp = client.post("/api/v1/flood/predict", json=bad_payload)
        assert resp.status_code == 422
        assert "traceback" not in resp.text.lower()

    def test_predict_out_of_range_value_returns_422(self, client):
        bad_payload = dict(VALID_FLOOD_PAYLOAD)
        bad_payload["humidity_pct"] = 250  # invalid, must be 0-100
        resp = client.post("/api/v1/flood/predict", json=bad_payload)
        assert resp.status_code == 422

    def test_predict_wrong_type_returns_422(self, client):
        bad_payload = dict(VALID_FLOOD_PAYLOAD)
        bad_payload["rainfall_mm"] = "a lot"
        resp = client.post("/api/v1/flood/predict", json=bad_payload)
        assert resp.status_code == 422


class TestUnifiedPredictEndpoint:
    def test_unified_dispatches_to_flood(self, client):
        payload = dict(VALID_FLOOD_PAYLOAD)
        payload["module"] = "flood"
        resp = client.post("/api/v1/predict", json=payload)
        assert resp.status_code == 200
        assert resp.json()["module"] == "flood"

    def test_unified_rejects_unknown_module(self, client):
        payload = dict(VALID_FLOOD_PAYLOAD)
        payload["module"] = "not_a_real_module"
        resp = client.post("/api/v1/predict", json=payload)
        assert resp.status_code == 422


class TestPredictionHistoryAndDetail:
    def test_history_reflects_new_prediction(self, client, auth_headers):
        client.post("/api/v1/flood/predict", json=VALID_FLOOD_PAYLOAD, headers=auth_headers)
        resp = client.get("/api/v1/predictions/history", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= 1
        assert body["results"][0]["module"] == "flood"

    def test_detail_returns_full_trace(self, client, auth_headers):
        client.post("/api/v1/flood/predict", json=VALID_FLOOD_PAYLOAD, headers=auth_headers)
        history = client.get("/api/v1/predictions/history", headers=auth_headers).json()
        pred_id = history["results"][0]["prediction_id"]
        resp = client.get(f"/api/v1/predictions/{pred_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["input_features"]["region"] == "Mumbai"
        assert "recommendations" in body

    def test_detail_unknown_id_returns_404(self, client):
        resp = client.get("/api/v1/predictions/999999")
        assert resp.status_code == 404


class TestDashboard:
    def test_overview_empty_state(self, client, auth_headers):
        resp = client.get("/api/v1/dashboard/overview", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total_assessments"] == 0

    def test_overview_after_prediction(self, client, auth_headers):
        client.post("/api/v1/flood/predict", json=VALID_FLOOD_PAYLOAD, headers=auth_headers)
        resp = client.get("/api/v1/dashboard/overview", headers=auth_headers)
        body = resp.json()
        assert body["total_assessments"] == 1

    def test_risk_distribution_shape(self, client):
        resp = client.get("/api/v1/dashboard/risk-distribution")
        assert resp.status_code == 200
        for level in ("LOW", "MODERATE", "HIGH", "CRITICAL"):
            assert level in resp.json()
