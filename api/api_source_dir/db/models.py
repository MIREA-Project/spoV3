import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from . import Base


class PFCc(Base):
    __tablename__ = "pfcc"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    proteins: Mapped[float] = mapped_column()
    fats: Mapped[float] = mapped_column()
    cb: Mapped[float] = mapped_column()
    calories: Mapped[float] = mapped_column()


class EatingType(Base):
    __tablename__ = "eating_type"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()


class Water(Base):
    __tablename__ = "water"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column()
    water_datetime: Mapped[datetime.datetime] = mapped_column()
    volume: Mapped[float] = mapped_column()


class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    pfcc_id: Mapped[int] = mapped_column(ForeignKey("pfcc.id"))


class UserEating(Base):
    __tablename__ = "user_eating"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column()
    create_date: Mapped[datetime.date] = mapped_column()
    eating_type_id: Mapped[int] = mapped_column(ForeignKey('eating_type.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))


class Steps(Base):
    __tablename__ = "steps"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column()
    steps_date: Mapped[datetime.date] = mapped_column()
    count: Mapped[int] = mapped_column()
