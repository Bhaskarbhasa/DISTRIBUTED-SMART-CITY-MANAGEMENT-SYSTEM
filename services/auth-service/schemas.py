from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from models import RoleEnum

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.VIEWER

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: RoleEnum
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    sub: str
    role: str
    jti: str
    exp: int

class UserRoleUpdate(BaseModel):
    role: RoleEnum
