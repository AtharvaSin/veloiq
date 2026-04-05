from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_actor
from app.exceptions import NotFoundError
from app.models.sales_escalation import SalesEscalation
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.sales_escalation import SalesEscalationRead, SalesEscalationUpdate
from app.services import escalations_service

router = APIRouter(prefix="/escalations", tags=["escalations"])

ALLOWED_SORT_FIELDS = {"created_at", "status", "opportunity_value", "resolved_at"}


@router.get("", response_model=PaginatedResponse[SalesEscalationRead])
def list_escalations(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    status: str | None = Query(None),
    customer_id: UUID | None = Query(None),
    assigned_to: str | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[SalesEscalationRead]:
    query = db.query(SalesEscalation)

    if status is not None:
        query = query.filter(SalesEscalation.status == status)
    if customer_id is not None:
        query = query.filter(SalesEscalation.customer_id == customer_id)
    if assigned_to is not None:
        query = query.filter(SalesEscalation.assigned_to == assigned_to)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "created_at"
    sort_column = getattr(SalesEscalation, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[SalesEscalationRead](
        data=[SalesEscalationRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{escalation_id}", response_model=SalesEscalationRead)
def get_escalation(
    escalation_id: UUID, db: Session = Depends(get_db)
) -> SalesEscalationRead:
    esc = (
        db.query(SalesEscalation)
        .filter(SalesEscalation.id == escalation_id)
        .first()
    )
    if esc is None:
        raise NotFoundError(entity="sales_escalation", entity_id=escalation_id)
    return SalesEscalationRead.model_validate(esc)


@router.patch("/{escalation_id}", response_model=SalesEscalationRead)
def update_escalation(
    escalation_id: UUID,
    payload: SalesEscalationUpdate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> SalesEscalationRead:
    esc = escalations_service.update_escalation(db, escalation_id, payload, actor)
    return SalesEscalationRead.model_validate(esc)
