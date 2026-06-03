from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from model.order_status import OrderStatus


class Order(BaseModel):
    id: Optional[int] = None
    user_id: int
    order_date: datetime
    shipping_address: str
    total_price: float
    status: OrderStatus