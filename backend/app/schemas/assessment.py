"""Assessment schemas — Read-only in Phase A (POST added in Phase C TCC workflow)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AssessmentRead(BaseModel):
    id: UUID
    match_result_id: UUID
    assessor_id: str
    impact_classification: str
    action_required: str
    reason_code: str
    notes: str | None
    decision: str
    decided_at: datetime
    signature_hash: str
    model_config = ConfigDict(from_attributes=True)
