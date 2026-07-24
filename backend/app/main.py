"""Application entry point.

Project rules and architecture: ../../AGENTS.md and ../../CONTEXT.md.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.modules.activities.router import router as activities_router
from app.modules.auth.router import router as auth_router
from app.modules.blog.router import router as blog_router
from app.modules.chat.router import router as chat_router
from app.modules.contact.router import router as contact_router
from app.modules.courses.router import router as courses_router
from app.modules.evidences.router import activity_router as activity_evidence_router
from app.modules.evidences.router import router as evidence_router
from app.modules.gamification.router import router as gamification_router
from app.modules.health.router import router as health_router
from app.modules.reports.router import router as reports_router
from app.modules.users.router import router as users_router


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings.evidence_storage_path.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict) and "code" in detail and "message" in detail:
        content = detail
    else:
        content = {"code": "http_error", "message": str(detail)}
    return JSONResponse(status_code=exc.status_code, content=content, headers=exc.headers)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    fields = [
        ".".join(str(part) for part in item["loc"] if part != "body")
        for item in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "code": "validation_error",
            "message": f"Revisa los campos enviados: {', '.join(fields)}.",
        },
    )


for module_router in (
    auth_router,
    users_router,
    courses_router,
    activities_router,
    activity_evidence_router,
    evidence_router,
    gamification_router,
    blog_router,
    contact_router,
    reports_router,
    chat_router,
    health_router,
):
    app.include_router(module_router, prefix=settings.api_prefix)
