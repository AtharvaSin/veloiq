"""SalesEscalation schemas — Read + Update (PATCH status/assigned_to only per CRUD matrix)."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SalesEscalationRead(BaseModel):
    id: UUID
    notification_id: UUID
    customer_id: UUID
    escalation_reason: str
    opportunity_value: Decimal
    assigned_to: str | None
    status: str
    created_at: datetime
    resolved_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class SalesEscalationUpdate(BaseModel):
    """Only `status` and `assigned_to` are mutable post-creation (compliance)."""

    model_config = ConfigDict(extra="forbid")

    status: str | None = None
    assigned_to: str | None = None
