from typing import List, Optional, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel, Field, root_validator

router = APIRouter()

class Material(BaseModel):
    name: str
    qty: float
    unit: Optional[str] = None
    price: Optional[float] = None
    unit_price: Optional[float] = Field(default=None, alias="unit_price")
    unit_price_nok: Optional[float] = Field(default=None, alias="unit_price_nok")

    @root_validator(pre=True)
    def _price_alias(cls, v):
        v = dict(v or {})
        if v.get("price") in (None, 0):
            up = v.get("unit_price") or v.get("unit_price_nok")
            if up is not None:
                v["price"] = up
        return v

class Workflow(BaseModel):
    task: str
    hours: float = 0.0

class Tool(BaseModel):
    name: str
    days: float = 0.0
    day_rate: Optional[float] = None

class Params(BaseModel):
    labor_rate: Optional[float] = None
    hourly_rate: Optional[float] = None  # alias iš UI
    material_markup: float = 0.0
    overhead_pct: float = 0.0
    profit_pct: float = 0.0
    overhead: Optional[float] = None     # alias iš UI
    profit: Optional[float] = None       # alias iš UI
    currency: str = "NOK"

    @root_validator(pre=True)
    def _aliases(cls, v):
        v = dict(v or {})
        if not v.get("labor_rate"):
            if v.get("hourly_rate") is not None:
                v["labor_rate"] = v["hourly_rate"]
        if "overhead_pct" not in v and v.get("overhead") is not None:
            v["overhead_pct"] = v["overhead"]
        if "profit_pct" not in v and v.get("profit") is not None:
            v["profit_pct"] = v["profit"]
        return v

class Body(BaseModel):
    materials: List[Material] = []
    workflow: List[Workflow] = []
    tools: List[Tool] = []
    params: Params

@router.post("/api/pricing/suggest")
async def pricing_suggest(body: Body) -> Dict[str, Any]:
    hours_total = float(sum((w.hours or 0) for w in body.workflow))
    labor = round(hours_total * float(body.params.labor_rate or 0), 2)

    materials_base = sum(((m.price or 0) * (m.qty or 0)) for m in body.materials)
    materials = round(materials_base * (1.0 + float(body.params.material_markup or 0)), 2)

    tools = 0.0  # (paprastai – 0; prireikus išplėsim)
    subtotal = round(labor + materials + tools, 2)

    overhead = round(subtotal * float(body.params.overhead_pct or 0), 2)
    profit   = round(subtotal * float(body.params.profit_pct   or 0), 2)
    total    = round(subtotal + overhead + profit, 2)

    return {
        "currency": body.params.currency,
        "total": total,
        "breakdown": {
            "materials": materials,
            "labor": labor,
            "tools": tools,
            "overhead": overhead,
            "profit": profit,
            "subtotal": subtotal,
        },
        "materials_total": materials,
        "labor_total": labor,
        "tools_total": tools,
        "overhead_total": overhead,
        "profit_total": profit,
        "subtotal": subtotal,
    }
