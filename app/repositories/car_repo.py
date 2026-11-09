from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.car import Car
from app.models.order import Order


class CarRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, car_id: int) -> Car | None:
        return self.db.get(Car, car_id)

    def get_by_plate(self, plate: str) -> Car | None:
        return self.db.scalar(select(Car).where(Car.plate_number == plate))

    def create(self, car: Car) -> Car:
        self.db.add(car)
        self.db.commit()
        self.db.refresh(car)
        return car

    def update(self, car: Car) -> Car:
        self.db.commit()
        self.db.refresh(car)
        return car

    def delete(self, car: Car) -> None:
        self.db.delete(car)
        self.db.commit()

    def list(
        self,
        brand: str | None = None,
        car_class: str | None = None,
        status: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Car], int]:
        stmt = select(Car)
        if brand:
            stmt = stmt.where(Car.brand.ilike(f"%{brand}%"))
        if car_class:
            stmt = stmt.where(Car.car_class == car_class)
        if status:
            stmt = stmt.where(Car.status == status)
        if min_price is not None:
            stmt = stmt.where(Car.price_per_day >= min_price)
        if max_price is not None:
            stmt = stmt.where(Car.price_per_day <= max_price)

        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list(self.db.scalars(stmt.offset(offset).limit(limit)))
        return items, total

    def is_available(self, car_id: int, start: date, end: date, exclude_order_id: int | None = None) -> bool:
        stmt = select(func.count()).select_from(Order).where(
            and_(
                Order.car_id == car_id,
                Order.status.in_(("new", "confirmed", "active")),
                Order.start_date < end,
                Order.end_date > start,
            )
        )
        if exclude_order_id is not None:
            stmt = stmt.where(Order.id != exclude_order_id)
        return (self.db.scalar(stmt) or 0) == 0