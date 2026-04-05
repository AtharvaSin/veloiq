from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CertStandardLink(Base):
    __tablename__ = "cert_standard_links"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    certificate_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("certificates.id"), nullable=False, index=True
    )
    standard_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    normalized_ref: Mapped[str] = mapped_column(String(200), nullable=False)
    base_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
