"""MatchResult schemas — Read-only in Phase A (Phase B matcher populates this table)."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MatchResultRead(BaseModel):
    id: UUID
    natos_standard_id: UUID
    cert_link_id: UUID
    similarity_score: Decimal
    levenshtein_score: Decimal | None
    jaro_winkler_score: Decimal | None
    token_set_score: Decimal | None
    confidence_tier: str
    status: str
    matched_at: datetime
    reviewed_at: datetime | None
    model_config = ConfigDict(from_attributes=True)
