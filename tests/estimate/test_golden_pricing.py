import json
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_update_override_labor_hour_no_vat():
    payload = {
        "materials": [{"name": "X", "quantity": 10}],  # materials_sum = 10 * 10 = 100
        "workflow": [{"task": "Y", "hours": 2}],       # labor_sum = 2 * 400 = 800
        "vat_pct": 0.0,
        "pricing": {"labor_hour": 400.0}
    }
    r = client.post("/api/v1/estimate/update", json=payload)
    assert r.status_code == 200
    j = r.json()
    # subtotal = 100 + 800 = 900
    # overhead 10% = 90
    # profit 10%   = (900 + 90) * 0.1 = 99
    # ex_vat = 1089, vat 0% = 0, grand_total = 1089
    assert j["materials_sum"] == 100.0
    assert j["labor_sum"] == 800.0
    assert j["grand_total_ex_vat"] == 1089.0
    assert j["vat_amount"] == 0.0
    assert j["grand_total"] == 1089.0
    assert j["rates_used"]["default_hourly_rate"] == 400.0

def test_update_override_all_params_with_vat():
    payload = {
        "materials": [{"name": "A", "quantity": 12}],    # 12 * 12.5 = 150
        "workflow": [{"task": "B", "hours": 8}],         # 8 * 450   = 3600
        "vat_pct": 0.25,
        "pricing": {
            "material_unit": 12.5,
            "labor_hour": 450.0,
            "overhead_pct": 0.08,
            "profit_pct": 0.12
        }
    }
    r = client.post("/api/v1/estimate/update", json=payload)
    assert r.status_code == 200
    j = r.json()
    # materials_sum = 150.0
    # labor_sum     = 3600.0
    # subtotal      = 3750.0
    # overhead      = 8% * 3750.0 = 300.0
    # profit        = 12% * (subtotal + overhead) = 0.12 * 4050.0 = 486.0
    # ex_vat        = 3750.0 + 300.0 + 486.0 = 4536.0
    # vat_amount    = 25% * 4536.0 = 1134.0
    # grand_total   = 4536.0 + 1134.0 = 5670.0
    assert j["materials_sum"] == 150.0
    assert j["labor_sum"] == 3600.0
    assert j["overhead"] == 300.0
    assert j["profit"] == 486.0
    assert j["grand_total_ex_vat"] == 4536.0
    assert j["vat_amount"] == 1134.0
    assert j["grand_total"] == 5670.0
    # patikrinam, kad „rates_used“ atspindi override’us
    assert j["rates_used"]["default_hourly_rate"] == 450.0
    assert j["rates_used"]["default_overhead_pct"] == 0.08
    assert j["rates_used"]["default_profit_pct"] == 0.12
