from typing import Optional

from pydantic import BaseModel


class Statistic(BaseModel):
    steps: Optional[int]
    calories: Optional[float]
    proteins: Optional[float]
    fats: Optional[float]
    cb: Optional[float]
    water: Optional[int]


class Product(BaseModel):
    name: str
    calories: float
    proteins: float
    fats: float
    cb: float
