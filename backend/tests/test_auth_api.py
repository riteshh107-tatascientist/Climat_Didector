"""Requires fastapi/sqlalchemy/httpx — see conftest.py docstring."""
import pytest


class TestSignup:
    def test_signup_success(self, client):
        resp = client.post("/api/v1/auth/signup", json={
            "email": "new@example.com", "password": "SecurePass1", "full_name": "New User",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "new@example.com"
        assert "password" not in body
        assert "password_hash" not in body

    def test_signup_duplicate_email_rejected(self, client):
        payload = {"email": "dup@example.com", "password": "SecurePass1"}
        client.post("/api/v1/auth/signup", json=payload)
        resp = client.post("/api/v1/auth/signup", json=payload)
        assert resp.status_code == 409

    def test_signup_weak_password_rejected(self, client):
        resp = client.post("/api/v1/auth/signup", json={
            "email": "weak@example.com", "password": "alllettersnodigits",
        })
        assert resp.status_code == 422

    def test_signup_invalid_email_rejected(self, client):
        resp = client.post("/api/v1/auth/signup", json={
            "email": "not-an-email", "password": "SecurePass1",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        client.post("/api/v1/auth/signup", json={"email": "log@example.com", "password": "SecurePass1"})
        resp = client.post("/api/v1/auth/login", json={"email": "log@example.com", "password": "SecurePass1"})
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        client.post("/api/v1/auth/signup", json={"email": "log2@example.com", "password": "SecurePass1"})
        resp = client.post("/api/v1/auth/login", json={"email": "log2@example.com", "password": "WrongPass1"})
        assert resp.status_code == 401

    def test_login_unknown_user(self, client):
        resp = client.post("/api/v1/auth/login", json={"email": "ghost@example.com", "password": "SecurePass1"})
        assert resp.status_code == 401


class TestProtectedRoutes:
    def test_me_requires_auth(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_with_valid_token(self, client, auth_headers):
        resp = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "judge@climateguard.test"

    def test_logout_revokes_token(self, client, auth_headers):
        resp = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert resp.status_code == 200
        resp2 = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp2.status_code == 401
