"""Unit tests for the FastAPI app factory in app/main.py.

These tests verify structural properties of the FastAPI app (title, version,
registered routes, middleware, exception handlers) without hitting the DB.
End-to-end HTTP behaviour is covered in tests/test_smoke.py.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.exceptions import (
    AuditViolationError,
    BusinessRuleError,
    NotFoundError,
    ValidationError,
)
from app.main import app, create_app


def test_create_app_returns_fastapi_instance() -> None:
    """create_app() returns a configured FastAPI instance."""
    new_app = create_app()
    assert isinstance(new_app, FastAPI)
    assert new_app.title == "VeloIQ API"
    assert new_app.version == "0.1.0"


def test_module_level_app_is_fastapi_instance() -> None:
    """The module-level `app` object is a FastAPI instance (uvicorn entry point)."""
    assert isinstance(app, FastAPI)
    assert app.title == "VeloIQ API"


def test_health_endpoint_is_registered() -> None:
    """The /health route is registered on the app."""
    paths = {route.path for route in app.routes}
    assert "/health" in paths


def test_all_api_v1_routers_are_registered() -> None:
    """All 8 resource routers are registered under /api/v1/."""
    paths = {route.path for route in app.routes}
    expected_prefixes = [
        "/api/v1/standards",
        "/api/v1/certificates",
        "/api/v1/customers",
        "/api/v1/matches",
        "/api/v1/assessments",
        "/api/v1/notifications",
        "/api/v1/escalations",
        "/api/v1/audit",
    ]
    for prefix in expected_prefixes:
        assert any(p.startswith(prefix) for p in paths), (
            f"No route registered for prefix {prefix}. Registered: {sorted(paths)}"
        )


def test_cors_middleware_is_configured() -> None:
    """CORSMiddleware is attached to the app."""
    middleware_classes = [m.cls for m in app.user_middleware]
    assert CORSMiddleware in middleware_classes


def test_all_custom_exception_handlers_are_registered() -> None:
    """All 4 VeloIQ custom exceptions have handlers registered."""
    handled = set(app.exception_handlers.keys())
    assert NotFoundError in handled
    assert ValidationError in handled
    assert BusinessRuleError in handled
    assert AuditViolationError in handled
