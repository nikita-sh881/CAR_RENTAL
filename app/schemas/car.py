from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CarBase(BaseModel):
    brand: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1950, le=2100)
    car_class: str = Field(min_length=1, max_length=30)
    plate_number: str = Field(min_length=3, max_length=15)
    price_per_day: Decimal = Field(gt=0)
    status: str = Field(default="available", pattern="^(available|rented|maintenance)$")


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    brand: str | None = Field(default=None, min_length=1, max_length=50)
    model: str | None = Field(default=None, min_length=1, max_length=50)
    year: int | None = Field(default=None, ge=1950, le=2100)
    car_class: str | None = Field(default=None, min_length=1, max_length=30)
    plate_number: str | None = Field(default=None, min_length=3, max_length=15)
    price_per_day: Decimal | None = Field(default=None, gt=0)
    status: str | None = Field(default=None, pattern="^(available|rented|maintenance)$")


class CarOut(CarBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

    @classmethod
    def from_orm_car(cls, car):
        return cls(
            id=car.id,
            brand=car.brand,
            model=car.model,
            year=car.year,
            car_class=car.car_class,
            plate_number=car.plate_number,
            price_per_day=car.price_per_day,
            status=car.status,
        )


class CarListOut(BaseModel):
    items: list[CarOut]
    total: int
    page: int
    page_size: int