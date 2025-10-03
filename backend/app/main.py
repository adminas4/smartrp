from fastapi import FastAPI
from app.api import agent, estimate, pricing, progress, admin

app = FastAPI()

# Pagrindiniai maršrutai (be papildomų prefiksų)
for r in (estimate.router, pricing.router, progress.router, admin.router, agent.router):
    app.include_router(r)

# Aliasai (kad veiktų ir /api/agent/ask bei /api/progress/healthz)
app.include_router(agent.router,   prefix="/api")
app.include_router(progress.router, prefix="/api/progress")
