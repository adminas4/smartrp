from __future__ import annotations

from typing import Optional, Dict, Any
from fastapi import APIRouter, status

router = APIRouter()

@router.get("/api/progress/list")
def progress_list(project_id: Optional[str] = None) -> Dict[str, Any]:
    return {"items": []}

@router.post("/api/progress/create", status_code=status.HTTP_201_CREATED)
def progress_create(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"ok": True, "id": "stub"}
