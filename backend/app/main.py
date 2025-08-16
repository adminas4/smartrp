from fastapi import FastAPI
from backend.app.api.estimate import analyze, update
from backend.app.api import health

app = FastAPI(title="SmartRP", version="1.0.0")

# Legacy maršrutai (suderinamumui)
app.include_router(analyze.router, prefix="/estimate")
app.include_router(update.router, prefix="/estimate")
app.include_router(health.router)  # suteikia /healthz ir /readyz

# Nauji v1 maršrutai
app.include_router(analyze.router, prefix="/api/v1/estimate")
app.include_router(update.router, prefix="/api/v1/estimate")
app.include_router(health.router, prefix="/api/v1")  # suteikia /api/v1/healthz ir /api/v1/readyz
