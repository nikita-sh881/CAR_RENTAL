from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_role
from app.database import get_db
from app.models.user import User
from app.schemas.car import CarCreate, CarListOut, CarOut, CarUpdate
from app.services.car_service import CarService

router = APIRouter(prefix="/api/cars", tags=["cars"])


@router.get("", response_model=CarListOut)
def list_cars(
    brand: str | None = None,
    car_class: str | None = None,
    status_: str | None = Query(default=None, alias="status"),
    min_price: float | None = None,
    max_price: float | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total = CarService(db).list(
        brand=brand,
        car_class=car_class,
        status=status_,
        min_price=min_price,
        max_price=max_price,
        offset=(page - 1) * page_size,
        limit=page_size,
    )
    return CarListOut(
        items=[CarOut.from_orm_car(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{car_id}", response_model=CarOut)
def get_car(car_id: int, db: Session = Depends(get_db)):
    return CarOut.from_orm_car(CarService(db).get(car_id))


@router.get("/{car_id}/availability")
def check_availability(car_id: int, start_date: date, end_date: date, db: Session = Depends(get_db)):
    available = CarService(db).check_availability(car_id, start_date, end_date)
    return {"car_id": car_id, "start_date": start_date, "end_date": end_date, "available": available}


@router.post("", response_model=CarOut, status_code=status.HTTP_201_CREATED)
def create_car(
    data: CarCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("manager", "admin")),
):
    return CarOut.from_orm_car(CarService(db).create(data))


@router.put("/{car_id}", response_model=CarOut)
def update_car(
    car_id: int,
    data: CarUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("manager", "admin")),
):
    return CarOut.from_orm_car(CarService(db).update(car_id, data))


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(
    car_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    CarService(db).delete(car_id)