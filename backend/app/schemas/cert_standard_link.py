from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CertStandardLinkBase(BaseModel):
    standard_ref: str
    normalized_ref: str
    base_number: str


class CertStandardLinkCreate(CertStandardLinkBase):
    certificate_id: UUID


class CertStandardLinkUpdate(BaseModel):
    standard_ref: str | None = None
    normalized_ref: str | None = None
    base_number: str | None = None


class CertStandardLinkRead(CertStandardLinkBase):
    id: UUID
    certificate_id: UUID
    linked_at: datetime
    model_config = ConfigDict(from_attributes=True)
