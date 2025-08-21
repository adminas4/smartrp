# backend/app/api/estimate/update.py
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body

from backend.app.schemas.estimate import EstimateResult
from backend.app.services.ai_estimate import AIEstimateService

router = APIRouter()


@router.post("/api/estimate/recalculate")
def recalculate_estimate(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Priima JSON:
      {
        "result": <EstimateResult>,
        "pricing": {...}?,   # optional overrides: material_unit, labor_hour, overhead_pct, profit_pct
        "vat_pct": 0.25?     # optional [0..1]
      }

    Grąžina breakdown suderintą su legacy v1/update: materials_sum, labor_sum, subtotal,
    overhead, profit, ex_vat, vat_amount, grand_total, grand_total_ex_vat, total_ex_vat,
    rates_used{... alias'ai}, currency="NOK".
    """
    # Parse ir validuojame visą sąmatą pagal mūsų Pydantic schemą:
    result = EstimateResult.model_validate(payload.get("result", {}))
    pricing: Optional[Dict[str, Any]] = payload.get("pricing")
    vat_pct: Optional[float] = payload.get("vat_pct")

    # Skaičiavimas
    return AIEstimateService.recalculate(result, pricing, vat_pct)


# --- Pasirinktinai: legacy trumpas kelias /update (jei kažkas dar kviečia seną endpoint'ą) ---
@router.post("/update")
def update_estimate_legacy(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Legacy alias į tą pačią logiką. Priima tą patį JSON kaip ir /api/estimate/recalculate.
    """
    result = EstimateResult.model_validate(payload.get("result", {}))
    pricing: Optional[Dict[str, Any]] = payload.get("pricing")
    vat_pct: Optional[float] = payload.get("vat_pct")
    return AIEstimateService.recalculate(result, pricing, vat_pct)
