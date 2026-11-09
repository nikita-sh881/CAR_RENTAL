from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_role
from app.database import get_db
from app.models.user import User
from app.schemas.order import OrderCreate, OrderListOut, OrderOut, OrderUpdateStatus
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=OrderListOut)
def list_orders(
    status_: str | None = Query(default=None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = OrderService(db).list(
        current_user,
        status=status_,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
    return OrderListOut(items=items, total=total, page=page, page_size=page_size)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = OrderService(db).get(order_id)
    if current_user.role.name == "client" and order.user_id != current_user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Forbidden")
    return order


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return OrderService(db).create(current_user, data)


@router.put("/{order_id}/status", response_model=OrderOut)
def change_status(
    order_id: int,
    data: OrderUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return OrderService(db).change_status(order_id, data.status, current_user)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    OrderService(db).cancel_by_client(order_id, current_user)