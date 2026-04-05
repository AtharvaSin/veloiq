from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.notification import Notification
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.notification import NotificationRead

router = APIRouter(prefix="/notifications", tags=["notifications"])

ALLOWED_SORT_FIELDS = {"sla_deadline", "sent_at", "status"}


@router.get("", response_model=PaginatedResponse[NotificationRead])
def list_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("sla_deadline"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    customer_id: UUID | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[NotificationRead]:
    query = db.query(Notification)

    if customer_id is not None:
        query = query.filter(Notification.customer_id == customer_id)
    if status is not None:
        query = query.filter(Notification.status == status)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "sla_deadline"
    sort_column = getattr(Notification, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[NotificationRead](
        data=[NotificationRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{notification_id}", response_model=NotificationRead)
def get_notification(
    notification_id: UUID, db: Session = Depends(get_db)
) -> NotificationRead:
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if notif is None:
        raise NotFoundError(entity="notification", entity_id=notification_id)
    return NotificationRead.model_validate(notif)
