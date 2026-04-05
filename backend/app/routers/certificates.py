from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_actor
from app.exceptions import NotFoundError
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateCreate, CertificateRead, CertificateUpdate
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.services import certificates_service

router = APIRouter(prefix="/certificates", tags=["certificates"])

ALLOWED_SORT_FIELDS = {
    "created_at",
    "updated_at",
    "certificate_number",
    "status",
    "expiry_date",
    "issue_date",
}


@router.get("", response_model=PaginatedResponse[CertificateRead])
def list_certificates(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    customer_id: UUID | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[CertificateRead]:
    query = db.query(Certificate)

    if customer_id is not None:
        query = query.filter(Certificate.customer_id == customer_id)
    if status is not None:
        query = query.filter(Certificate.status == status)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "created_at"
    sort_column = getattr(Certificate, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[CertificateRead](
        data=[CertificateRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{certificate_id}", response_model=CertificateRead)
def get_certificate(certificate_id: UUID, db: Session = Depends(get_db)) -> CertificateRead:
    cert = db.query(Certificate).filter(Certificate.id == certificate_id).first()
    if cert is None:
        raise NotFoundError(entity="certificate", entity_id=certificate_id)
    return CertificateRead.model_validate(cert)


@router.post("", response_model=CertificateRead, status_code=201)
def create_certificate(
    payload: CertificateCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> CertificateRead:
    cert = certificates_service.create_certificate(db, payload, actor)
    return CertificateRead.model_validate(cert)


@router.patch("/{certificate_id}", response_model=CertificateRead)
def update_certificate(
    certificate_id: UUID,
    payload: CertificateUpdate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> CertificateRead:
    cert = certificates_service.update_certificate(db, certificate_id, payload, actor)
    return CertificateRead.model_validate(cert)
