from app.api import health as health_router
from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="SmartRP API")

@app.get("/api/progress/health")
def health():
    return {"status": "ok"}

# Pricing router (neprivalomas – jei nepavyksta, API vis tiek kyla)
try:
    from backend.pricing.router import router as pricing_router
    app.include_router(pricing_router)
app.include_router(health_router.router)
except Exception as e:
    import logging
    logging.getLogger("uvicorn.error").warning(f"Pricing router not loaded: {e}")
