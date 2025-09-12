from fastapi import APIRouter, Response
from os import getenv

router = APIRouter()

@router.get("/health")
def health_ping():
    return Response(status_code=204)

@router.get("/healthz.json")
def healthz_json():
    am = getenv("OPENAI_MODEL_ANALYZE", "")
    pm = getenv("OPENAI_MODEL_PRICING", "")
    return {
        "ok": True,
        "status": "ok",
        "mode": "full",
        "model": am or pm,
        "analyze_model": am,
        "pricing_model": pm,
        "has_key": bool(getenv("OPENAI_API_KEY")),
    }

@router.get("/healthz")
def healthz_plain():
    return healthz_json()
from fastapi.responses import FileResponse

@router.get("/demo.pdf")
def demo_pdf():
    return FileResponse("/srv/smartrp/frontend/dist/demo.pdf",
                        media_type="application/pdf",
                        filename="demo.pdf")
