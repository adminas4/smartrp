from fastapi import APIRouter
from backend.app.schemas.estimate import (
    EstimateAnalyzeRequest,
    EstimateResponse,
)

router = APIRouter()

# --- Naujas API: POST /analyze ---
@router.post(
    "/analyze",
    response_model=EstimateResponse,
    response_model_exclude_none=True,
    summary="Analyze free-text description into a draft estimate",
    description=(
        "Priima tekstinį aprašą ir grąžina **stub** sąmatos juodraštį su bent vienu "
        "materials ir vienu workflow įrašu. Numatyta valiuta: **NOK**."
    ),
)
def analyze_estimate(req: EstimateAnalyzeRequest):
    """
    Stub logika: pagal aprašą grąžinam minimalų draft'ą.
    Ateityje čia galės būti GPT/NLP analizė + kainynų lookup.
    """
    text = (req.description or "").lower()
    if "roof" in text or "stog" in text:
        materials = [{"name": "Roof tiles", "quantity": 250}]
        workflow = [{"task": "Roofing", "hours": 16}]
    else:
        materials = [{"name": "Generic material", "quantity": 10}]
        workflow = [{"task": "Generic work", "hours": 4}]

    return {
        "currency": req.currency or "NOK",
        "materials": materials,
        "workflow": workflow,
    }

# --- Suderinamumas: legacy GET /analyze ---
@router.get(
    "/analyze",
    response_model=EstimateResponse,
    response_model_exclude_none=True,
    summary="(Legacy) Analyze endpoint",
    description="Suderinamumo vardan grąžina minimalų sąmatos stub’ą.",
)
def analyze_estimate_legacy():
    return {
        "currency": "NOK",
        "materials": [{"name": "Generic material", "quantity": 10}],
        "workflow": [{"task": "Generic work", "hours": 4}],
    }
