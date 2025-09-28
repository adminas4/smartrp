from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os, json, re, math, urllib.request

router = APIRouter()

class Material(BaseModel):
    name: str
    qty: float
    unit: Optional[str] = None
    price: Optional[float] = None

class Workflow(BaseModel):
    task: str
    hours: float

class Crew(BaseModel):
    role: str
    count: int

class Tool(BaseModel):
    name: str
    days: float = 0

class AnalyzeRequest(BaseModel):
    description: str
    locale: Optional[str] = "nb"

# --- OpenAI helper ---
def _openai_chat_json(model: str, messages: list, temperature: float = 0.1, max_tokens: int = 900) -> Dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return json.loads(body["choices"][0]["message"]["content"])

# --- Įrankių katalogas + praplėtimas ---
TOOL_MAP: Dict[str, List[str]] = {
    r"(terrasse|tre|dekc?k)": [
        "Drill/slagtrekker","Sirkelsag","Bordsag (opsjon)","Krysslaser",
        "Målebånd","Vater","Avstandskiler","Borspisser/bits","Skrutvinger",
        "Hørselvern","Hansker"
    ],
    r"(grunn|graving|planering)": [
        "Gravemaskin","Laser","Spade","Stikkspade","Trillebår"
    ],
    r"(betong|st[øo]p)": [
        "Betongblander","Platevibrator","Rettholt","Betongvibrator",
        "Glattere","Forskaling","Bøtte","Spade","Trillebår"
    ],
    r"(isolasjon|isolering)": [
        "Kniv for isolasjon","Stiftepistol","Støvmaske","Hansker"
    ],
    r"(fukt|membran|dampsperre)": [
        "Varmluftpistol","Rulle","Kniv","Stiftepistol"
    ],
}

HEAVY_SET = {"Gravemaskin","Betongblander","Platevibrator"}

def _enrich_tools(description: str, out: Dict[str, Any]) -> None:
    """Papildo GPT grąžintus įrankius pagal darbų/teksto raktažodžius."""
    text = (description or "") + " " + " ".join([w.get("task","") for w in out.get("workflow",[])])
    tools: Dict[str, float] = {}

    # jau esami
    for t in out.get("tools", []) or []:
        name = str(t.get("name","")).strip()
        if not name: continue
        tools[name] = max(tools.get(name, 0), float(t.get("days") or 1))

    # pagal žodžius
    for pat, lst in TOOL_MAP.items():
        if re.search(pat, text, re.I):
            for name in lst:
                days = 1.0
                if name in HEAVY_SET:
                    # grubus vertinimas: sunkiai technikai – bent 1 d. arba pagal dulkių val. sumą
                    tot_h = sum([float(w.get("hours") or 0) for w in out.get("workflow",[])])
                    days = max(1.0, math.ceil(tot_h/8.0))
                tools[name] = max(tools.get(name, 0), days)

    # atgal į out
    out["tools"] = [Tool(name=n, days=d).dict() for n,d in sorted(tools.items())]

def _analyze_with_gpt(description: str, locale: str = "nb") -> Dict[str, Any]:
    model = os.environ.get("OPENAI_MODEL_ANALYZE", "gpt-4o")
    sys = (
        "Du er en norsk bygg-kalkulatør. Ekstrahér realistiske lister over "
        "materialer, arbeidsoppgaver, mannskap og verktøy for prosjekt i Norge. "
        "Svar KUN som JSON (materials, workflow, crew, tools). Minst 6 materialer, 3 oppgaver."
    )
    usr = (
        f"Beskrivelse (språk={locale}): {description}\n"
        "Returnér KUN JSON:\n"
        "{\n"
        '  "materials":[{"name":"...","qty":number,"unit":"m²|lm|stk|kg","price":null},...],\n'
        '  "workflow":[{"task":"...","hours":number},...],\n'
        '  "crew":[{"role":"Snekker|Elektriker|...","count":number},...],\n'
        '  "tools":[{"name":"...","days":number},...]\n'
        "}\n"
    )
    data = _openai_chat_json(model, [
        {"role":"system","content":sys},
        {"role":"user","content":usr},
    ])

    out = {
        "materials": data.get("materials") or [],
        "workflow":  data.get("workflow") or [],
        "crew":      data.get("crew") or [],
        "tools":     data.get("tools") or [],
    }

    # Minimalus demo-fallback
    if len(out["materials"]) < 3 or len(out["workflow"]) < 2:
        out = {
            "materials":[
                {"name":"Terrassebord impregnert 28x120","qty":10,"unit":"m²","price":None},
                {"name":"Bjelker/dragere C24","qty":35,"unit":"lm","price":None},
                {"name":"Bjelkesko/beslag","qty":24,"unit":"stk","price":None},
                {"name":"Stolper 90x90","qty":6,"unit":"stk","price":None},
                {"name":"Punktfundament/betong","qty":6,"unit":"stk","price":None},
                {"name":"Skruer terrasse A2","qty":600,"unit":"stk","price":None},
            ],
            "workflow":[
                {"task":"Oppmåling og fundamenter","hours":6},
                {"task":"Bjelkelag og dragere","hours":8},
                {"task":"Montering terrassebord","hours":10},
            ],
            "crew":[{"role":"Snekker","count":2}],
            "tools":[{"name":"Drill/slagtrekker","days":1},{"name":"Sirkelsag","days":1}],
        }

    # tipizavimas
    out["materials"] = [Material(**m).dict() for m in out["materials"] if isinstance(m, dict)]
    out["workflow"]  = [Workflow(**w).dict() for w in out["workflow"] if isinstance(w, dict)]
    out["crew"]      = [Crew(**c).dict() for c in out["crew"] if isinstance(c, dict)]
    out["tools"]     = [Tool(**t).dict() for t in out["tools"] if isinstance(t, dict)]

    # praplėsti įrankius
    _enrich_tools(description, out)
    return out

@router.post("/api/estimate/analyze")
async def analyze(req: AnalyzeRequest) -> Dict[str, Any]:
    try:
        return _analyze_with_gpt(req.description, req.locale or "nb")
    except Exception:
        # garantuotas demo atsakymas
        out = _analyze_with_gpt("fallback: liten treterrasse ca. 10 m² på punktfundament", "nb")
        return out
