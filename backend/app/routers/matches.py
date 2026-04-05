from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.match_result import MatchResult
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.match_result import MatchResultRead

router = APIRouter(prefix="/matches", tags=["matches"])

ALLOWED_SORT_FIELDS = {"matched_at", "similarity_score", "confidence_tier", "status"}


@router.get("", response_model=PaginatedResponse[MatchResultRead])
def list_matches(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("matched_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    confidence_tier: str | None = Query(None),
    status: str | None = Query(None),
    natos_standard_id: UUID | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[MatchResultRead]:
    query = db.query(MatchResult)

    if confidence_tier is not None:
        query = query.filter(MatchResult.confidence_tier == confidence_tier)
    if status is not None:
        query = query.filter(MatchResult.status == status)
    if natos_standard_id is not None:
        query = query.filter(MatchResult.natos_standard_id == natos_standard_id)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "matched_at"
    sort_column = getattr(MatchResult, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[MatchResultRead](
        data=[MatchResultRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{match_id}", response_model=MatchResultRead)
def get_match(match_id: UUID, db: Session = Depends(get_db)) -> MatchResultRead:
    match = db.query(MatchResult).filter(MatchResult.id == match_id).first()
    if match is None:
        raise NotFoundError(entity="match_result", entity_id=match_id)
    return MatchResultRead.model_validate(match)
