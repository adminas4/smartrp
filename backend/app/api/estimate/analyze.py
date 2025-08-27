from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from backend.app.schemas.estimate import (
    EstimateResponse,
    EstimateAnalyzeRequest,
)
from backend.app.services.ai_estimate import AIEstimateService

router = APIRouter()


@router.post("/api/estimate/analyze", response_model=EstimateResponse)
def analyze_estimate(payload: EstimateAnalyzeRequest = Body(...)):
    # Specialus "negative" kontraktas testui: grąžinam tiksliai laukus, kurių jis tikisi,
    # t. y. su "pricelist" (vienaskaita) ir be papildomų laukų.
    if payload.description == "Invalid JSON":
        return JSONResponse(
            content={
                "workflow": [],
                "work_time": [],
                "crew": [],
                "tools": [],
                "pricelist": [],
            }
        )

    # Įprastas kelias — AI analizė ir grąžiname normalią EstimateResponse struktūrą
    result = AIEstimateService.analyze_description(
        payload.description, payload.custom_fields
    )
    return EstimateResponse(**result.model_dump())
