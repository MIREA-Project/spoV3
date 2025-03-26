from pydantic import BaseModel


class Statistic(BaseModel):
    steps: int
    calories: float
    proteins: float
    fats: float
    cb: float
    water: int


class Product(BaseModel):
    name: str
    calories: float
    proteins: float
    fats: float
    cb: float
