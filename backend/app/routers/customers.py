from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_actor
from app.exceptions import NotFoundError
from app.models.customer import Customer
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services import customers_service

router = APIRouter(prefix="/customers", tags=["customers"])

ALLOWED_SORT_FIELDS = {"created_at", "company_name", "customer_number", "country"}


@router.get("", response_model=PaginatedResponse[CustomerRead])
def list_customers(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    country: str | None = Query(None),
    sales_area: str | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedResponse[CustomerRead]:
    query = db.query(Customer)

    if country is not None:
        query = query.filter(Customer.country == country)
    if sales_area is not None:
        query = query.filter(Customer.sales_area == sales_area)

    total = query.count()

    sort_field = sort if sort in ALLOWED_SORT_FIELDS else "created_at"
    sort_column = getattr(Customer, sort_field)
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())

    offset = (page - 1) * limit
    items = query.offset(offset).limit(limit).all()

    return PaginatedResponse[CustomerRead](
        data=[CustomerRead.model_validate(item) for item in items],
        pagination=PaginationMeta(
            page=page,
            limit=limit,
            total=total,
            total_pages=ceil(total / limit) if total > 0 else 0,
        ),
    )


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)) -> CustomerRead:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise NotFoundError(entity="customer", entity_id=customer_id)
    return CustomerRead.model_validate(customer)


@router.post("", response_model=CustomerRead, status_code=201)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> CustomerRead:
    customer = customers_service.create_customer(db, payload, actor)
    return CustomerRead.model_validate(customer)


@router.patch("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: UUID,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    actor: str = Depends(get_current_actor),
) -> CustomerRead:
    customer = customers_service.update_customer(db, customer_id, payload, actor)
    return CustomerRead.model_validate(customer)
