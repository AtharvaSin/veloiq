"""AuditLog schema — Read-only (append-only table, no Create/Update/Delete exposed)."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    actor: str
    details: dict[str, Any]
    ip_address: str | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
