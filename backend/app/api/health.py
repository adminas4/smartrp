from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
async def healthz():
    return {"status": "ok"}


@router.get("/readyz")
async def readyz():
    return {"status": "ready"}


@router.get("/v1/healthz")
async def v1_healthz():
    return {"status": "ok"}


@router.get("/v1/readyz")
async def v1_readyz():
    return {"status": "ready"}
