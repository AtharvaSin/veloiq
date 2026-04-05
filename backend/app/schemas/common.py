"""Shared response envelopes and error schemas used across all routers."""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination envelope metadata returned with every list response."""

    page: int = Field(..., ge=1, description="1-indexed current page")
    limit: int = Field(..., ge=1, le=500, description="Items per page")
    total: int = Field(..., ge=0, description="Total matching records")
    total_pages: int = Field(..., ge=0, description="Total pages available")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper: `{data: [...], pagination: {...}}`."""

    data: list[T]
    pagination: PaginationMeta


class ErrorResponse(BaseModel):
    """Standard error body. Maps to NotFoundError, BusinessRuleError, AuditViolationError."""

    model_config = ConfigDict(extra="allow")

    error: str
    code: str
    entity: str | None = None
    id: str | None = None
    rule: str | None = None


class ValidationErrorResponse(BaseModel):
    """422 response body for Pydantic/business validation failures."""

    error: str
    code: str = "VALIDATION_ERROR"
    fields: dict[str, str] = Field(default_factory=dict)
