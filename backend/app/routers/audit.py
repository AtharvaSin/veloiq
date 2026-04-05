from datetime import datetime
from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogRead
from app.schemas.common import PaginatedResponse, PaginationMeta

router = APIRouter(prefix="/audit", tags=["audit"])

ALLOWED_SORT_FIELDS = {"created_at", "entity_type", "actor", "action"}


@router.get("", response_model=PaginatedResponse[AuditLogRead])
def list_audit(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    entity_type: str | None = Query(None),
    entity_id: UUID | None = Query(None),
    actor: str | None = Query(None),
    action: str | None = Query(None),
    from_: datetime | None = Query(None, alias="from"),
    to: datetime | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AuditLogRead]:
    query = db.query(AuditLog)

    if entity_type is not None:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id is not None:
        query = query.filter(AuditLog.entity_id == entity_id)
    if actor is not None:
        query = query.filter(AuditLog.actor == actor)
    if action is not None:
        query = query.filter(AuditLog.action == action)
    if from_ is not None:
        query = query.filter(AuditLog.created_at >= from_)
    if to is not None:
        query = query.filter(AuditLog.created_at <= to)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "created_at"
    sort_column = getattr(AuditLog, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[AuditLogRead](
        data=[AuditLogRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{audit_id}", response_model=AuditLogRead)
def get_audit_entry(audit_id: UUID, db: Session = Depends(get_db)) -> AuditLogRead:
    entry = db.query(AuditLog).filter(AuditLog.id == audit_id).first()
    if entry is None:
        raise NotFoundError(entity="audit_log", entity_id=audit_id)
    return AuditLogRead.model_validate(entry)
