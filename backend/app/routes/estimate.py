from fastapi import APIRouter, HTTPException
from backend.app.schemas.estimate import EstimateResult
from backend.app.services.ai_estimate import AIAnalyzer

router = APIRouter()


@router.post("/api/estimate/analyze", response_model=EstimateResult)
def analyze_estimate(description: str, custom_fields: dict = None):
    try:
        result = AIAnalyzer.analyze_description(description, custom_fields)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/estimate/recalculate", response_model=EstimateResult)
def recalculate_estimate(result: EstimateResult):
    try:
        updated_result = AIAnalyzer.recalculate(result)
        return updated_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
