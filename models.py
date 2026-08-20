from pydantic import BaseModel, Field
from enum import Enum

class OrderStatus(str, Enum):
    NEW = "new"
    COOKING = "cooking"
    READY = "ready"

class OrderCreate(BaseModel):
    table_id: int = Field(gt=0, description="Номер стола")
    items: list[str] = Field(min_length=1, description="Список блюд")
    total_price: float = Field(gt=0, description="Итоговая сумма")

class OrderResponse(BaseModel):
    id: int
    table_id: int
    items: list[str]
    total_price: float
    status: OrderStatus