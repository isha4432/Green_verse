from typing import Optional
from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: str = "farmer" # farmer or head

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    role: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
