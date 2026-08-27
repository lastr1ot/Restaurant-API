from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class OrderStatus(StrEnum):
    NEW = "new"
    COOKING = "cooking"
    READY = "ready"


class OrderItem(BaseModel):
    name: str = Field(..., description="Название блюда")
    quantity: int = Field(ge=1, description="Колво")
    price: Decimal = Field(ge=0, description="Цена за единицу")


class OrderCreate(BaseModel):
    table_id: int = Field(gt=0, description="Номер стола")
    items: list[OrderItem] = Field(min_length=1, description="Список блюд")
    total_price: Decimal = Field(gt=0, description="Итоговая сумма")


class OrderResponse(BaseModel):
    id: int
    table_id: int
    items: list[OrderItem]
    total_price: Decimal
    status: OrderStatus

    model_config = ConfigDict(use_enum_values=True)
