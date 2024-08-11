import enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


class Role(str, enum.Enum):
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    nickname: str
    role: Role

    @validator("nickname")
    def validate_nickname(cls, v):
        if len(v) < 3:
            raise ValueError("닉네임은 3자 이상이어야 합니다.")
        return v


class UserCreate(UserBase):
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        if not any(char.isupper() for char in v):
            raise ValueError("비밀번호에는 대문자가 하나 이상 포함되어야 합니다.")
        return v


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    password: Optional[str] = None
    role: Optional[Role] = None

    @validator("password", always=True, pre=True)
    def validate_password(cls, v):
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        if not any(char.isupper() for char in v):
            raise ValueError("비밀번호에는 대문자가 하나 이상 포함되어야 합니다.")
        return v

    class Config:
        from_attributes = True


class UserInDB(UserRead):
    hashed_password: str

    class Config:
        from_attributes = True
