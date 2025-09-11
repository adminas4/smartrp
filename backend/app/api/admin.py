from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
import os
from app.flags import get_mode, set_mode

router = APIRouter(prefix="/admin", tags=["admin"])

class ModeIn(BaseModel):
    mode: str  # "demo" | "full"

def _auth(tok: Optional[str]):
    if tok != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=401, detail="unauthorized")

@router.get("/mode")
def read_mode():
    return {"mode": get_mode()}

@router.post("/mode")
def write_mode(body: ModeIn, x_admin_token: Optional[str] = Header(None)):
    _auth(x_admin_token)
    set_mode(body.mode)
    return {"mode": get_mode()}
