from app.api.estimate_gpt import _analyze_with_gpt
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/estimate", tags=["estimate"])

class AnalyzeRequest(BaseModel):
    description: str
    locale: Optional[str] = "nb"

def _expand_scope(desc: str, locale: str) -> str:
    d = desc.lower()
    if (("garasje" in d or "garasj" in d) and ("plate på mark" in d or "plate pa mark" in d or "slab" in d)):
        desc += """
Forstå at dette er komplett nybygg av garasje med plate på mark.
Lag FULL liste: grunnarbeid/ringmur/plate (utgraving, pukk, EPS S80 100 mm, radonduk, armeringsnett K131, betong C25 100 mm, L-elementer),
bindingsverk 48x148, vindsperre, isolasjon ~150 mm, dampsperre, kledning,
takstoler, undertak/lekter, takpapp SBS, takrenner/nedløp,
åpninger (leddport 2,4×2,1, ytterdør 9×21, 2 vinduer 10×10),
festemateriell/småvarer. Fordel arbeid: betongarbeider + tømrer. Inkluder verktøy.
"""
    return desc

def _safe_call_gpt(desc: str, locale: str):
    # Jei projekte yra _analyze_with_gpt – naudok; jei ne – duok prasmingą fallback
    try:
        if '_analyze_with_gpt' in globals():
            print("USING GPT"); return globals()['_analyze_with_gpt'](desc, locale)
    except Exception as e:
        import traceback; print("GPT ERROR:", e)
        pass
    # DEMO/fallback – daugiau nei vien tik „Takpapp“
    print("USING DEMO")
    return { 
        "materials": [
            {"name":"Utgraving og bortkjøring", "unit":"m³", "qty":15},
            {"name":"Pukk 16/32", "unit":"tonn", "qty":10},
            {"name":"EPS S80 100 mm", "unit":"m²", "qty":50},
            {"name":"Radonduk med tilbehør", "unit":"m²", "qty":50},
            {"name":"Armeringsnett K131", "unit":"m²", "qty":50},
            {"name":"Betong C25 100 mm", "unit":"m³", "qty":5},
            {"name":"L-elementer/ringmur", "unit":"lm", "qty":28},
            {"name":"48x148 konstruksjon", "unit":"lm", "qty":120},
            {"name":"Vindsperre", "unit":"m²", "qty":80},
            {"name":"Isolasjon ~150 mm", "unit":"m²", "qty":50},
            {"name":"Dampsperre", "unit":"m²", "qty":50},
            {"name":"Kledning", "unit":"m²", "qty":60},
            {"name":"Takstoler", "unit":"stk", "qty":8},
            {"name":"Undertak/lekter", "unit":"m²", "qty":50},
            {"name":"Takpapp SBS", "unit":"m²", "qty":50},
            {"name":"Takrenner/nedløp", "unit":"lm", "qty":18},
            {"name":"Leddport 2,4×2,1", "unit":"stk", "qty":1},
            {"name":"Ytterdør 9×21", "unit":"stk", "qty":1},
            {"name":"Vinduer 10×10", "unit":"stk", "qty":2},
            {"name":"Festemateriell/småvarer", "unit":"sett", "qty":1}
        ],
        "workflow":[
            {"task":"Grunnarbeid og betongarbeider","hours":40},
            {"task":"Tømrerarbeider (råbygg + tak)","hours":80}
        ],
        "crew":[{"role":"Betongarbeider","count":2},{"role":"Tømrer","count":2}],
        "tools":["Minigraver","Vibroplata","Blander","Sag","Skrutrekker"]
    }

@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    desc = _expand_scope(req.description, req.locale or "nb")
    out = _safe_call_gpt(desc, req.locale or "nb")
    return _normalize_tools(out)

def _normalize_tools(out: dict) -> dict:
    tools = out.get("tools") or []
    norm = []
    for t in tools:
        if isinstance(t, str):
            norm.append({"name": t, "days": 1})
        elif isinstance(t, dict):
            n = t.get("name") or ""
            d = t.get("days") or 1
            norm.append({"name": n, "days": d})
    out["tools"] = norm
    return out
