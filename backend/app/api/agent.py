from __future__ import annotations
from typing import Optional, Dict, Any
from fastapi import APIRouter
try:
    from app.flags import is_full_mode
except Exception:
    def is_full_mode():
        import os
        return os.getenv("OPENAI_MODE","demo").lower()=="full"
from pydantic import BaseModel
import os
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

router = APIRouter()

class AskIn(BaseModel):
    question: str
    project_id: Optional[str] = None

@router.post("/agent/ask")
def agent_ask(body: AskIn) -> Dict[str, Any]:
    mode  = os.environ.get("AGENT_MODE", "demo").lower()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o")
    q_raw = (body.question or "").strip()
    q     = q_raw.lower()

    if ("model" in q) or ("modelis" in q):
        return {"answer": model}

    if (not is_full_mode()) or (not os.environ.get("OPENAI_API_KEY")) or (OpenAI is None):
        return {"answer": "Klausimą gavau."}

    try:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        sys = ("Tu esi SmartRP asistentas. Atsakinėk trumpai. "
               "Neskelbk modelio ar API detalių. Jei klausia apie kainas, primink skiltį 'Kainų paieška'.")
        resp = client.responses.create(
            model=model,
            temperature=float(os.environ.get("OPENAI_TEMPERATURE","0.2")),
            input=[
                {"role":"system","content":[{"type":"input_text","text": sys}]},
                {"role":"user","content":[{"type":"input_text","text": q_raw}]},
            ],
        )
        return {"answer": resp.output_text}
    except Exception:
        return {"answer": "Klausimą gavau."}
