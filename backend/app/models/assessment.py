from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Assessment(Base):
    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint(
            "impact_classification IN ('no_change','administrative','minor_technical','major_technical','safety_critical')",
            name="ck_assessments_impact",
        ),
        CheckConstraint(
            "action_required IN ('reconfirm','retest','suspend','withdraw')",
            name="ck_assessments_action",
        ),
        CheckConstraint(
            "decision IN ('approved','rejected','escalated')",
            name="ck_assessments_decision",
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    match_result_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("match_results.id"), nullable=False, index=True
    )
    assessor_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    impact_classification: Mapped[str] = mapped_column(String(30), nullable=False)
    action_required: Mapped[str] = mapped_column(String(30), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    signature_hash: Mapped[str] = mapped_column(String(128), nullable=False)
