from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Standard(Base):
    __tablename__ = "standards"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    ac_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    replaced_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    normalized_code: Mapped[str] = mapped_column(String(100), nullable=False)
    base_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    version_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    committee: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ics_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
