from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CertificateBase(BaseModel):
    certificate_number: str
    customer_id: UUID
    product_description: str
    status: str
    issue_date: date
    expiry_date: date


class CertificateCreate(CertificateBase):
    pass


class CertificateUpdate(BaseModel):
    product_description: str | None = None
    status: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None


class CertificateRead(CertificateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
