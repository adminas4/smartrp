from __future__ import annotations
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from openai import OpenAI

router = APIRouter()
_client: Optional[OpenAI] = None

def client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        _client = OpenAI(api_key=api_key)
    return _client

class AskIn(BaseModel):
    question: str
    project_id: Optional[str] = None

@router.post("/api/agent/ask")
def agent_ask(body: AskIn) -> Dict[str, Any]:
    try:
        sys = ("Tu esi SmartRP asist. Atsakinėk trumpai. "
               "Kai prašo kainų, primink mygtuką 'Kainų paieška'.")
        user = body.question.strip()
        resp = client().responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": [{"type":"text","text": sys}]},
                {"role": "user",   "content": [{"type":"text","text": user}]},
            ],
        )
        return {"answer": resp.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
