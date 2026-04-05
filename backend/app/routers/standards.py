from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_actor
from app.exceptions import NotFoundError
from app.models.standard import Standard
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.standard import StandardCreate, StandardRead, StandardUpdate
from app.services import standards_service

router = APIRouter(prefix="/standards", tags=["standards"])

ALLOWED_SORT_FIELDS = {"created_at", "updated_at", "ac_code", "status", "base_number"}


@router.get("", response_model=PaginatedResponse[StandardRead])
def list_standards(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    status: str | None = Query(None),
    committee: str | None = Query(None),
    base_number: str | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[StandardRead]:
    query = db.query(Standard)

    if status is not None:
        query = query.filter(Standard.status == status)
    if committee is not None:
        query = query.filter(Standard.committee == committee)
    if base_number is not None:
        query = query.filter(Standard.base_number == base_number)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "created_at"
    sort_column = getattr(Standard, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[StandardRead](
        data=[StandardRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{standard_id}", response_model=StandardRead)
def get_standard(standard_id: UUID, db: Session = Depends(get_db)) -> StandardRead:
    standard = db.query(Standard).filter(Standard.id == standard_id).first()
    if standard is None:
        raise NotFoundError(entity="standard", entity_id=standard_id)
    return StandardRead.model_validate(standard)


@router.post("", response_model=StandardRead, status_code=201)
def create_standard(
    payload: StandardCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> StandardRead:
    standard = standards_service.create_standard(db, payload, actor)
    return StandardRead.model_validate(standard)


@router.patch("/{standard_id}", response_model=StandardRead)
def update_standard(
    standard_id: UUID,
    payload: StandardUpdate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> StandardRead:
    standard = standards_service.update_standard(db, standard_id, payload, actor)
    return StandardRead.model_validate(standard)
