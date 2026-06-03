from pydantic import BaseModel

class AuthResponse(BaseModel):
    jwt_token: str