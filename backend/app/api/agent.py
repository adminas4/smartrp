from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/agent", tags=["agent"])

class Ask(BaseModel):
    question: Optional[str] = None
    q: Optional[str] = None
    model: Optional[str] = None

    def normalized_question(self) -> str:
        return (self.question or self.q or "").strip()

@router.post("/ask")
async def ask(req: Ask):
    q = req.normalized_question().lower()
    if q == "ping":
        return {"answer": "Pong! Kaip galiu padėti?", "model": req.model or "auto"}
    return {"answer": f"Girdžiu: {req.normalized_question()}", "model": req.model or "auto"}
