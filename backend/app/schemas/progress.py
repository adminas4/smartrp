from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class ProgressCreate(BaseModel):
    project_id: str = Field(..., example="proj-123")
    task_id: Optional[str] = Field(None, example="task-001")
    percent: float = Field(..., ge=0, le=100, example=25.0)
    note: Optional[str] = Field(None, example="Sienos rėmas pastatytas")
    photo_url: Optional[str] = None

class ProgressItem(ProgressCreate):
    id: str
    timestamp: datetime

class ProgressList(BaseModel):
    items: List[ProgressItem]
