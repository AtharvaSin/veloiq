from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StandardBase(BaseModel):
    ac_code: str
    title: str
    status: str
    replaced_by: str | None = None
    committee: str | None = None
    ics_code: str | None = None


class StandardCreate(StandardBase):
    source_payload: dict[str, Any]


class StandardUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    replaced_by: str | None = None
    committee: str | None = None
    ics_code: str | None = None


class StandardRead(StandardBase):
    id: UUID
    normalized_code: str
    base_number: str
    version_year: int | None
    ingested_at: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
