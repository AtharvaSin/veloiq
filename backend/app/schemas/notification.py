"""Notification schemas — Read-only in Phase A (Phase D dispatcher populates this table)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    id: UUID
    assessment_id: UUID
    customer_id: UUID
    template_language: str
    subject: str
    body_html: str
    status: str
    sent_at: datetime | None
    delivered_at: datetime | None
    opened_at: datetime | None
    clicked_at: datetime | None
    sla_deadline: datetime
    model_config = ConfigDict(from_attributes=True)
