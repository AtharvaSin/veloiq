"""FastAPI application factory for VeloIQ.

Wires together configuration, middleware, exception handlers, and routers into a
single ASGI application. Exposes both a `create_app()` factory (for testing and
programmatic use) and a module-level `app` instance (for uvicorn / Docker).
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import (
    AuditViolationError,
    BusinessRuleError,
    NotFoundError,
    ValidationError,
)
from app.routers import (
    assessments,
    audit,
    certificates,
    customers,
    escalations,
    matches,
    notifications,
    standards,
)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application.

    Returns a fully-wired FastAPI instance with CORS, exception handlers,
    health check, and all /api/v1 routers registered.
    """
    app = FastAPI(
        title="VeloIQ API",
        version="0.1.0",
        description="TÜV Rheinland Standards Automation Platform",
    )

    # --- CORS ------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Exception handlers ----------------------------------------------
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "error": str(exc),
                "code": exc.code,
                "entity": exc.entity,
                "id": str(exc.entity_id),
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": exc.message,
                "code": exc.code,
                "fields": exc.fields,
            },
        )

    @app.exception_handler(BusinessRuleError)
    async def business_rule_handler(request: Request, exc: BusinessRuleError) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "error": exc.message,
                "code": exc.code,
                "rule": exc.rule,
            },
        )

    @app.exception_handler(AuditViolationError)
    async def audit_violation_handler(
        request: Request, exc: AuditViolationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": exc.message, "code": exc.code},
        )

    # --- Routers ---------------------------------------------------------
    for module in (
        standards,
        customers,
        certificates,
        matches,
        assessments,
        notifications,
        escalations,
        audit,
    ):
        app.include_router(module.router, prefix=settings.api_v1_prefix)

    # --- Health check ----------------------------------------------------
    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        """Liveness probe — returns 200 OK with a status payload."""
        return {"status": "ok"}

    return app


app = create_app()
