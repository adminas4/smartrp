# backend/app/services/recalc.py
from backend.app.schemas.estimate import UpdateRequest
from backend.app.services.config import load_base_config

def recalculate_totals(update_request: UpdateRequest):
    cfg = load_base_config()

    # baziniai tarifai
    hourly_rate = cfg["default_hourly_rate"]
    overhead_pct = cfg["default_overhead_pct"]
    profit_pct = cfg["default_profit_pct"]
    vat_pct = update_request.vat_pct if update_request.vat_pct is not None else cfg["default_vat_pct"]
    material_unit = 10.0  # demo bazė, kol neturim kainyno faile

    # override'ai iš užklausos (jei pateikti)
    pr = update_request.pricing
    if pr:
        if pr.labor_hour is not None:
            hourly_rate = pr.labor_hour
        if pr.overhead_pct is not None:
            overhead_pct = pr.overhead_pct
        if pr.profit_pct is not None:
            profit_pct = pr.profit_pct
        if pr.material_unit is not None:
            material_unit = pr.material_unit

    # skaičiavimai
    materials_sum = sum(item.quantity * material_unit for item in update_request.materials)
    labor_sum = sum(step.hours * hourly_rate for step in update_request.workflow)

    subtotal = materials_sum + labor_sum
    overhead = subtotal * overhead_pct
    profit = (subtotal + overhead) * profit_pct
    grand_total_ex_vat = subtotal + overhead + profit
    vat_amount = grand_total_ex_vat * vat_pct
    grand_total = grand_total_ex_vat + vat_amount

    return {
        "currency": "NOK",
        "totals": round(grand_total, 2),
        "materials_sum": round(materials_sum, 2),
        "labor_sum": round(labor_sum, 2),
        "overhead": round(overhead, 2),
        "profit": round(profit, 2),
        "grand_total_ex_vat": round(grand_total_ex_vat, 2),
        "vat_pct": vat_pct,
        "vat_amount": round(vat_amount, 2),
        "grand_total": round(grand_total, 2),
        "rates_used": {
            "default_hourly_rate": hourly_rate,
            "default_overhead_pct": overhead_pct,
            "default_profit_pct": profit_pct,
            "default_vat_pct": vat_pct,
            "material_unit_demo": material_unit
        }
    }
