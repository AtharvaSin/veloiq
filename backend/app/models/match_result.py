from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MatchResult(Base):
    __tablename__ = "match_results"
    __table_args__ = (
        CheckConstraint(
            "confidence_tier IN ('auto_match','expert_review','manual_triage')",
            name="ck_match_results_tier",
        ),
        UniqueConstraint("natos_standard_id", "cert_link_id", name="uq_match_results_pair"),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    natos_standard_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("standards.id"), nullable=False
    )
    cert_link_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("cert_standard_links.id"), nullable=False
    )
    similarity_score: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    levenshtein_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3), nullable=True)
    jaro_winkler_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3), nullable=True)
    token_set_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3), nullable=True)
    confidence_tier: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    matched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
