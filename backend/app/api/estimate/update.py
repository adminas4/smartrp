import time
import uuid
from fastapi import APIRouter
from backend.app.schemas.estimate import UpdateRequest, UpdateResponse
from backend.app.services.recalc import recalculate_totals

router = APIRouter()

@router.post(
    "/update",
    response_model=UpdateResponse,
    response_model_exclude_none=True,
    summary="Recalculate estimate totals",
    description=(
        "Apskaičiuoja sąmatos suvestines pagal pateiktas medžiagas, darbo žingsnius ir pasirenkamus "
        "tarifų override’us (`pricing`). Numatyta valiuta: **NOK**. "
        "PVM (`vat_pct`) leidžiamas intervale **0.0..1.0**."
    ),
)
def update_estimate(update_request: UpdateRequest):
    result = recalculate_totals(update_request)

    # ---- papildytos įspėjimų taisyklės ----
    warnings = []
    if any(m.quantity == 0 for m in update_request.materials):
        warnings.append("Some materials have 0 quantity.")
    if any(w.hours == 0 for w in update_request.workflow):
        warnings.append("Some workflow steps have 0 hours.")

    # Anomalijų patikros pagal rezultatą
    ex_vat = result.get("grand_total_ex_vat", 0) or 0
    mat = result.get("materials_sum", 0) or 0
    lab = result.get("labor_sum", 0) or 0
    vat_pct = result.get("vat_pct", None)

    if ex_vat > 1_000_000:
        warnings.append("Grand total (ex VAT) is unusually high (> 1,000,000 NOK).")
    if mat > 0 and lab / mat > 10:
        warnings.append("Labor-to-materials ratio is unusually high (> 10x).")
    if vat_pct == 0:
        warnings.append("VAT is set to 0%. Confirm tax handling.")

    # Įdedam metaduomenis
    result.update({
        "schema_version": "1.0",
        "calc_id": str(uuid.uuid4()),
        "timestamp": int(time.time()),
        "warnings": warnings or None,
    })
    return result
