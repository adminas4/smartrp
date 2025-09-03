# backend/app/main.py
from typing import Any, Dict

from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import health as health_router
from app.routes.pricing import router as pricing_router
from app.routes.status import router as status_router
from app.services.ai_estimate import analyze_description, recalc

app = FastAPI(title="SmartRP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://smartrp.org", "http://localhost", "http://127.0.0.1"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# status + pricing maršrutai
app.include_router(status_router)
app.include_router(pricing_router)
app.include_router(health_router.router)


@app.post("/api/estimate/analyze")
def analyze(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    desc = (payload or {}).get("description", "") or ""
    return analyze_description(desc)


@app.post("/api/estimate/recalculate")
def recalculate(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    # priimame pliką JSON (materials/workflow/crew/tools)
    return recalc(payload)
