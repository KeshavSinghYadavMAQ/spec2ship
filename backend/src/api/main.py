"""FastAPI app, `/v1` versioned router mounting, and exception handlers (T016).

Maps validation and domain errors to the `ProblemDetail` schema so API consumers get a
consistent error shape across all endpoints.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.middleware.rate_limit import RateLimitMiddleware
from src.api.routers import alerts, inventory, replenishment
from src.infrastructure.config import get_settings
from src.infrastructure.observability import configure_observability
from src.schemas.errors import ProblemDetail

configure_observability()

settings = get_settings()

app = FastAPI(title="Retail Replenishment V1 API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors: dict[str, list[str]] = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:]) or "body"
        errors.setdefault(field, []).append(error["msg"])
    problem = ProblemDetail(title="Validation Error", status=422, errors=errors)
    return JSONResponse(status_code=422, content=problem.model_dump(), media_type="application/problem+json")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict):
        content = detail
    else:
        content = ProblemDetail(title=str(detail), status=exc.status_code, detail=str(detail)).model_dump()
    return JSONResponse(status_code=exc.status_code, content=content, media_type="application/problem+json")


v1_router_prefix = "/v1"
app.include_router(inventory.router, prefix=v1_router_prefix)
app.include_router(alerts.router, prefix=v1_router_prefix)
app.include_router(replenishment.router, prefix=v1_router_prefix)


@app.get("/healthz", tags=["ops"])
async def healthz() -> dict:
    return {"status": "ok"}
