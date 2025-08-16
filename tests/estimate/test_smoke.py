import sys, os
# Du katalogus aukštyn iki projekto root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_analyze_estimate():
    response = client.get("/estimate/analyze")
    assert response.status_code == 200
    assert response.json()["currency"] == "NOK"

def test_update_estimate():
    update_data = {
        "materials": [{"name": "Steel", "quantity": 100}],
        "workflow": [{"task": "Welding", "hours": 5}]
    }
    response = client.post("/estimate/update", json=update_data)
    assert response.status_code == 200
    assert response.json()["currency"] == "NOK"
