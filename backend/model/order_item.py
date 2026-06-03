from typing import Optional
from pydantic import BaseModel


class OrderItem(BaseModel):
    id: Optional[int] = None
    order_id: int
    item_id: int
    quantity: int
    price_per_item: float