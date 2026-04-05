from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.assessment import Assessment
from app.schemas.assessment import AssessmentRead
from app.schemas.common import PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/assessments", tags=["assessments"])

ALLOWED_SORT_FIELDS = {"decided_at", "assessor_id", "decision", "impact_classification"}


@router.get("", response_model=PaginatedResponse[AssessmentRead])
def list_assessments(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("decided_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    assessor_id: str | None = Query(None),
    decision: str | None = Query(None),
    impact_classification: str | None = Query(None),
    match_result_id: UUID | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AssessmentRead]:
    query = db.query(Assessment)

    if assessor_id is not None:
        query = query.filter(Assessment.assessor_id == assessor_id)
    if decision is not None:
        query = query.filter(Assessment.decision == decision)
    if impact_classification is not None:
        query = query.filter(Assessment.impact_classification == impact_classification)
    if match_result_id is not None:
        query = query.filter(Assessment.match_result_id == match_result_id)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "decided_at"
    sort_column = getattr(Assessment, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[AssessmentRead](
        data=[AssessmentRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{assessment_id}", response_model=AssessmentRead)
def get_assessment(assessment_id: UUID, db: Session = Depends(get_db)) -> AssessmentRead:
    a = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if a is None:
        raise NotFoundError(entity="assessment", entity_id=assessment_id)
    return AssessmentRead.model_validate(a)
