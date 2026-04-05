import pytest
from pydantic import ValidationError

from app.schemas.common import (
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    ValidationErrorResponse,
)


def test_pagination_meta_computes_valid_envelope() -> None:
    meta = PaginationMeta(page=1, limit=50, total=147, total_pages=3)
    assert meta.page == 1
    assert meta.limit == 50
    assert meta.total == 147
    assert meta.total_pages == 3


def test_pagination_meta_rejects_negative_page() -> None:
    with pytest.raises(ValidationError):
        PaginationMeta(page=0, limit=50, total=147, total_pages=3)


def test_paginated_response_wraps_arbitrary_data() -> None:
    resp = PaginatedResponse[dict](
        data=[{"id": 1}, {"id": 2}],
        pagination=PaginationMeta(page=1, limit=2, total=10, total_pages=5),
    )
    assert len(resp.data) == 2
    assert resp.pagination.total == 10


def test_error_response_shape() -> None:
    err = ErrorResponse(
        error="Standard not found",
        code="NOT_FOUND",
        entity="standard",
        id="abc-123",
    )
    assert err.code == "NOT_FOUND"
    assert err.entity == "standard"


def test_error_response_requires_error_and_code() -> None:
    with pytest.raises(ValidationError):
        ErrorResponse(error="missing code")  # type: ignore[call-arg]


def test_validation_error_response_captures_field_errors() -> None:
    err = ValidationErrorResponse(
        error="Validation failed",
        code="VALIDATION_ERROR",
        fields={"ac_code": "required", "status": "must be ISO stage code"},
    )
    assert err.fields["ac_code"] == "required"
