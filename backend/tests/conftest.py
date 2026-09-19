"""
Shared pytest fixtures.

NOTE: these fixtures require fastapi/sqlalchemy/httpx to be installed
(`pip install -r backend/requirements-dev.txt`). They could not be
executed inside the authoring sandbox, which has no fastapi/sqlalchemy
available and no network to install them — see README "Environment
Limitations". The logic-only test modules (test_security.py,
test_risk_engine.py, test_recommendation_engine.py, test_preprocessing.py,
test_predictors.py) import no FastAPI/SQLAlchemy code and DID run and
pass in that sandbox; run the full suite (`pytest backend/tests`) in a
normal environment to exercise these API-level tests too.
"""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.orm import Base
from app.models.db import get_db
from app.main import app


@pytest.fixture()
def test_db_session():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestingSessionLocal
    app.dependency_overrides.clear()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def client(test_db_session):
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers(client):
    client.post("/api/v1/auth/signup", json={
        "email": "judge@climateguard.test", "password": "TestPass123",
        "full_name": "Test Judge",
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": "judge@climateguard.test", "password": "TestPass123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
