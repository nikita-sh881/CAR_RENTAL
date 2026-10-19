from decimal import Decimal

from sqlalchemy import CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Car(Base):
    __tablename__ = "cars"
    __table_args__ = (CheckConstraint("price_per_day > 0", name="ck_cars_price_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[int] = mapped_column(nullable=False)
    car_class: Mapped[str] = mapped_column("class", String(30), nullable=False, index=True)
    plate_number: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    price_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="available", index=True)

    orders: Mapped[list["Order"]] = relationship(back_populates="car")