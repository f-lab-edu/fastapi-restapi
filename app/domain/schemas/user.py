import re
from datetime import datetime

from pydantic import BaseModel, Field, validator


class UserBase(BaseModel):
    nickname: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator("password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    password: str = None
    nickname: str = None
