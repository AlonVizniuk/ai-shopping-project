from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: Optional[int] = None
    first_name: str
    last_name: str
    email: str
    phone: str
    country: str
    city: str
    username: str
    hashed_password: str