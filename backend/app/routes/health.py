from fastapi import APIRouter, Response
router = APIRouter()

@router.get("/health")
def health():
    return Response(status_code=204)

@router.get("/api/progress/health")
def progress_health():
    return Response(status_code=204)
