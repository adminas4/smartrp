from datetime import datetime
from typing import Dict, List
from uuid import uuid4
from ..schemas.progress import ProgressCreate, ProgressItem, ProgressList

# Paprastas in-memory saugojimas MVP'ui (vėliau pakeisim į DB)
_DB: Dict[str, List[ProgressItem]] = {}

def add_progress(data: ProgressCreate) -> ProgressItem:
    item = ProgressItem(
        id=str(uuid4()),
        timestamp=datetime.utcnow(),
        **data.model_dump(),
    )
    _DB.setdefault(data.project_id, []).append(item)
    return item

def list_progress(project_id: str) -> ProgressList:
    return ProgressList(items=_DB.get(project_id, []))
