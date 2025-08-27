from fastapi import APIRouter, Query
from ..schemas.progress import ProgressCreate, ProgressItem, ProgressList
from ..services.progress import add_progress, list_progress

router = APIRouter()

@router.get("/api/progress/health")
def progress_health():
    return {"status": "ok"}

@router.post("/api/progress/create", response_model=ProgressItem)
def progress_create(payload: ProgressCreate):
    return add_progress(payload)

@router.get("/api/progress/list", response_model=ProgressList)
def progress_list(project_id: str = Query(..., description="Project ID")):
    return list_progress(project_id)
