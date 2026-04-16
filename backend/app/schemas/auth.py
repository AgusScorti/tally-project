"""
Schemas Pydantic - Autenticación y usuarios
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# ==================== USER ====================

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== AUTH ====================

class TokenData(BaseModel):
    sub: str  # Usuario ID como string
    exp: Optional[int] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
