import pytest
from httpx import AsyncClient
from backend.app.main import app


@pytest.mark.asyncio
async def test_estimate_analyze_contract():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/estimate/analyze", json={"description": "Test description"}
        )
        assert response.status_code == 200
        assert "workflow" in response.json()


@pytest.mark.asyncio
async def test_estimate_analyze_negative():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/estimate/analyze", json={"description": "Invalid JSON"}
        )
        assert response.status_code == 200
        assert response.json() == {
            "workflow": [],
            "work_time": [],
            "crew": [],
            "tools": [],
            "pricelist": [],
        }
