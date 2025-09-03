from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_progress_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_progress_create_and_list():
    payload = {
        "project_id": "proj-123",
        "percent": 10.5,
        "note": "Start",
    }
    r = client.post("/api/progress/create", json=payload)
    assert r.status_code == 200, r.text
    item = r.json()
    assert item["project_id"] == "proj-123"
    assert item["percent"] == 10.5

    r2 = client.get("/api/progress/list", params={"project_id": "proj-123"})
    assert r2.status_code == 200
    data = r2.json()
    assert len(data["items"]) >= 1
