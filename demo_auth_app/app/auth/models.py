"""Data models and schemas for authentication."""
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
import re

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password at least 8 chars")
    confirm_password: str = Field(..., description="Password confirmation")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        value = value.strip()
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError("Username can only contain alphanumeric characters and underscores.")
        return value

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, value: str, info) -> str:
        password = info.data.get("password")
        if password and value != password:
            raise ValueError("Passwords do not match.")
        return value

class UserLoginRequest(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Account password")

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    created_at: str

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class MessageResponse(BaseModel):
    message: str
    success: bool = True

