"""User-related Pydantic models"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str  # "admin", "sdr", "assignee"


class UserUpdate(BaseModel):
    """Schema for updating user"""
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    name: str
    email: str
    phone: Optional[str]
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserRegisterRequest(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str
    name: str
    role: Optional[str] = "sdr"
    phone: Optional[str] = None
