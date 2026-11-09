from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.car import Car
from app.repositories.car_repo import CarRepository
from app.schemas.car import CarCreate, CarUpdate


class CarService:
    def __init__(self, db: Session):
        self.cars = CarRepository(db)

    def create(self, data: CarCreate) -> Car:
        if self.cars.get_by_plate(data.plate_number):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Plate number already exists")
        car = Car(**data.model_dump())
        return self.cars.create(car)

    def get(self, car_id: int) -> Car:
        car = self.cars.get_by_id(car_id)
        if car is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
        return car

    def list(self, **filters) -> tuple[list[Car], int]:
        return self.cars.list(**filters)

    def update(self, car_id: int, data: CarUpdate) -> Car:
        car = self.get(car_id)
        payload = data.model_dump(exclude_unset=True)
        if "plate_number" in payload:
            other = self.cars.get_by_plate(payload["plate_number"])
            if other and other.id != car.id:
                raise HTTPException(status_code=409, detail="Plate number already exists")
        for field, value in payload.items():
            setattr(car, field, value)
        return self.cars.update(car)

    def delete(self, car_id: int) -> None:
        car = self.get(car_id)
        self.cars.delete(car)

    def check_availability(self, car_id: int, start: date, end: date) -> bool:
        if end <= start:
            raise HTTPException(status_code=400, detail="end_date must be greater than start_date")
        self.get(car_id)
        return self.cars.is_available(car_id, start, end)