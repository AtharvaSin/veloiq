"""Pydantic v2 schemas for request/response validation — mirrors app.models structure."""

from app.schemas.assessment import AssessmentRead
from app.schemas.audit_log import AuditLogRead
from app.schemas.cert_standard_link import (
    CertStandardLinkBase,
    CertStandardLinkCreate,
    CertStandardLinkRead,
    CertStandardLinkUpdate,
)
from app.schemas.certificate import (
    CertificateBase,
    CertificateCreate,
    CertificateRead,
    CertificateUpdate,
)
from app.schemas.common import (
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    ValidationErrorResponse,
)
from app.schemas.customer import (
    CustomerBase,
    CustomerCreate,
    CustomerRead,
    CustomerUpdate,
)
from app.schemas.match_result import MatchResultRead
from app.schemas.notification import NotificationRead
from app.schemas.sales_escalation import (
    SalesEscalationRead,
    SalesEscalationUpdate,
)
from app.schemas.standard import (
    StandardBase,
    StandardCreate,
    StandardRead,
    StandardUpdate,
)

__all__ = [
    "AssessmentRead",
    "AuditLogRead",
    "CertStandardLinkBase",
    "CertStandardLinkCreate",
    "CertStandardLinkRead",
    "CertStandardLinkUpdate",
    "CertificateBase",
    "CertificateCreate",
    "CertificateRead",
    "CertificateUpdate",
    "CustomerBase",
    "CustomerCreate",
    "CustomerRead",
    "CustomerUpdate",
    "ErrorResponse",
    "MatchResultRead",
    "NotificationRead",
    "PaginatedResponse",
    "PaginationMeta",
    "SalesEscalationRead",
    "SalesEscalationUpdate",
    "StandardBase",
    "StandardCreate",
    "StandardRead",
    "StandardUpdate",
    "ValidationErrorResponse",
]
