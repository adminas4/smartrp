from __future__ import annotations

from fastapi import FastAPI
from backend.app.api import health as health_router
from backend.app.api import progress as progress_router

app = FastAPI(title="SmartRP API")

# Health routes
app.include_router(health_router.router)
app.include_router(progress_router.router)

# Pricing router (optional – API kyla ir be jo)
try:
    from backend.pricing.router import router as pricing_router
    app.include_router(pricing_router)
except Exception as e:
    import logging
    logging.getLogger("uvicorn.error").warning(f"Pricing router not loaded: {e}")
