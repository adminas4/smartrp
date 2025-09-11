from fastapi import APIRouter, Response
from app.flags import get_mode

router = APIRouter(prefix="/progress", tags=["progress"])

@router.get("/health", status_code=204)
def health():
    return Response(status_code=204)

@router.get("/healthz")
def healthz():
    return {"status": "ok", "mode": get_mode(), "model": "gpt-4o"}
