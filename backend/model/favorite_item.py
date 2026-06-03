from typing import Optional
from pydantic import BaseModel


class FavoriteItem(BaseModel):
    id: Optional[int] = None
    user_id: int
    item_id: int