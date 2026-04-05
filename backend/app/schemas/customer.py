from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class CustomerBase(BaseModel):
    customer_number: str
    company_name: str
    country: str
    sales_area: str
    language: str
    contact_name: str | None = None
    contact_email: EmailStr | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    company_name: str | None = None
    country: str | None = None
    sales_area: str | None = None
    language: str | None = None
    contact_name: str | None = None
    contact_email: EmailStr | None = None


class CustomerRead(CustomerBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
