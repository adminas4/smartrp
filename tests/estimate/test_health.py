from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz():
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_v1_healthz():
    response = client.get("/v1/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_v1_readyz():
    response = client.get("/v1/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
