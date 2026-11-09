from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.car import Car
from app.models.order import Order
from app.models.user import User
from app.repositories.car_repo import CarRepository
from app.repositories.order_repo import OrderRepository
from app.schemas.order import OrderCreate

ALLOWED_TRANSITIONS = {
    "new": {"confirmed", "cancelled"},
    "confirmed": {"active", "cancelled"},
    "active": {"completed"},
    "completed": set(),
    "cancelled": set(),
}


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.orders = OrderRepository(db)
        self.cars = CarRepository(db)

    def _calc_total(self, car: Car, start: date, end: date) -> Decimal:
        days = (end - start).days
        if days <= 0:
            raise HTTPException(status_code=400, detail="Rental period must be at least 1 day")
        return Decimal(car.price_per_day) * Decimal(days)

    def create(self, user: User, data: OrderCreate) -> Order:
        car = self.cars.get_by_id(data.car_id)
        if car is None:
            raise HTTPException(status_code=404, detail="Car not found")
        if car.status != "available":
            raise HTTPException(status_code=409, detail="Car is not available")
        if not self.cars.is_available(car.id, data.start_date, data.end_date):
            raise HTTPException(status_code=409, detail="Car is already booked for the selected period")

        total = self._calc_total(car, data.start_date, data.end_date)
        order = Order(
            user_id=user.id,
            car_id=car.id,
            start_date=data.start_date,
            end_date=data.end_date,
            total_price=total,
            status="new",
        )
        return self.orders.create(order)

    def get(self, order_id: int) -> Order:
        order = self.orders.get_by_id(order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    def list(self, user: User, **filters) -> tuple[list[Order], int]:
        if user.role.name == "client":
            filters["user_id"] = user.id
        return self.orders.list(**filters)

    def change_status(self, order_id: int, new_status: str, actor: User) -> Order:
        order = self.get(order_id)

        if actor.role.name == "client":
            if order.user_id != actor.id:
                raise HTTPException(status_code=403, detail="Forbidden")
            if new_status != "cancelled":
                raise HTTPException(status_code=403, detail="Client can only cancel own order")

        allowed = ALLOWED_TRANSITIONS.get(order.status, set())
        if new_status not in allowed:
            raise HTTPException(status_code=409, detail=f"Cannot transition {order.status} -> {new_status}")

        if new_status == "active":
            car = self.cars.get_by_id(order.car_id)
            if car is None or car.status != "available":
                raise HTTPException(status_code=409, detail="Car is not available to start rental")
            car.status = "rented"
            self.db.add(car)
        if new_status in ("completed", "cancelled"):
            car = self.cars.get_by_id(order.car_id)
            if car is not None and car.status == "rented":
                car.status = "available"
                self.db.add(car)

        order.status = new_status
        self.db.commit()
        self.db.refresh(order)
        return order

    def cancel_by_client(self, order_id: int, user: User) -> Order:
        order = self.get(order_id)
        if order.user_id != user.id:
            raise HTTPException(status_code=403, detail="Forbidden")
        if order.status not in ("new", "confirmed"):
            raise HTTPException(status_code=409, detail="Order cannot be cancelled in current status")
        order.status = "cancelled"
        self.db.commit()
        self.db.refresh(order)
        return order