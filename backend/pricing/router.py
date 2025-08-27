from typing import List, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
from .agent import fetch_offers, load_whitelist

router = APIRouter()

class Item(BaseModel):
    name: str

class Body(BaseModel):
    items: List[Item]

@router.post("/api/pricing/suggest")
async def pricing_suggest(body: Body) -> Dict[str, Any]:
    wl = load_whitelist()
    out = []
    for it in body.items:
        offers = await fetch_offers(it.name, domains=wl)
        out.append({"query": it.name, "offers": offers})
    return {"results": out}
