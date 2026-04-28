from pydantic import BaseModel
from datetime import datetime


class OrderCreate(BaseModel):
    shipping_address: str


class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float
    product_title: str | None = None


class OrderOut(BaseModel):
    id: int
    total_amount: float
    status: str
    shipping_address: str
    created_at: datetime
    items: list[OrderItemOut]

    model_config = {"from_attributes": True}
