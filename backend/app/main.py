from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SmartRP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

from app.api import agent, estimate, pricing, progress, admin  # noqa

for r in (agent.router, estimate.router, pricing.router, progress.router, admin.router):
    app.include_router(r, prefix="/api")
from app.api.pricing import router as pricing_router
app.include_router(pricing_router)

from app.api.estimate import router as estimate_router
app.include_router(estimate_router)
