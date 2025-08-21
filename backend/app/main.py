from fastapi import FastAPI
from backend.app.api.estimate import legacy as legacy_router
from backend.app.api.estimate import analyze as analyze_router
from backend.app.api.estimate import update as update_router

# --- middleware importai ---
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json

app = FastAPI(title="SmartRP API")

# Legacy pirmas — kad jo path'ai būtų pasiekiami
app.include_router(legacy_router.router)
app.include_router(analyze_router.router)
app.include_router(update_router.router)


# --- Middleware: visada užtikrina default_hourly_rate atsakyme iš /api/v1/estimate/update ---
class EnsureDefaultHourlyRateMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if (
            request.url.path == "/api/v1/estimate/update"
            and request.method.upper() == "POST"
        ):
            response = await call_next(request)
            try:
                # perkonstruojam JSON, pridedam trūkstamus laukus jei reikia
                if isinstance(response, JSONResponse) and isinstance(
                    response.body, (bytes, bytearray)
                ):
                    data = json.loads(response.body.decode("utf-8"))
                    if isinstance(data, dict):
                        labor = 400.0
                        rates = data.get("rates_used")
                        if isinstance(rates, dict):
                            labor = rates.get("labor_hour", labor)
                        if "default_hourly_rate" not in data:
                            data["default_hourly_rate"] = labor
                        data.setdefault("hourly_rate", labor)
                        data.setdefault("currency", "NOK")
                        # atstatom JSONResponse su tais pačiais antraštėmis
                        headers = dict(response.headers)
                        response = JSONResponse(
                            content=data,
                            status_code=response.status_code,
                            headers=headers,
                        )
            except Exception:
                # jei kas nors nepavyksta, grąžinam originalų atsakymą
                return response
            return response
        return await call_next(request)


app.add_middleware(EnsureDefaultHourlyRateMiddleware)


# Sveikatos patikros, kurių prašo testai
@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}


@app.get("/v1/healthz")
def v1_healthz():
    return {"status": "ok"}


@app.get("/v1/readyz")
def v1_readyz():
    return {"status": "ready"}


# Paliekam ir /health (jei reikės)
@app.get("/health")
def health():
    return {"status": "ok"}
