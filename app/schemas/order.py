from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrderCreate(BaseModel):
    car_id: int
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be greater than start_date")
        return self


class OrderUpdateStatus(BaseModel):
    status: str = Field(pattern="^(confirmed|active|completed|cancelled|new)$")


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    car_id: int
    start_date: date
    end_date: date
    total_price: Decimal
    status: str
    created_at: datetime


class OrderListOut(BaseModel):
    items: list[OrderOut]
    total: int
    page: int
    page_size: int