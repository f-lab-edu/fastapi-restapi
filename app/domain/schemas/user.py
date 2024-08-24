import enum
from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, validator


class Role(str, enum.Enum):
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    role: Role


class UserCreate(UserBase):
    userid: str
    nickname: str
    password: str

    @staticmethod
    def validate_password_strength(password: str) -> str:
        if len(password) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        if not any(char.isupper() for char in password):
            raise ValueError("비밀번호에는 대문자가 하나 이상 포함되어야 합니다.")
        return password

    _validate_password = validator("password", allow_reuse=True)(
        validate_password_strength
    )


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    password: Optional[str] = None
    role: Optional[Role] = None

    @staticmethod
    def validate_password_strength(password: str) -> str:
        if len(password) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        if not any(char.isupper() for char in password):
            raise ValueError("비밀번호에는 대문자가 하나 이상 포함되어야 합니다.")
        return password

    _validate_password = validator("password", pre=True, allow_reuse=True)(
        validate_password_strength
    )

    class Config:
        from_attributes = True


class UserInDB(UserRead):
    hashed_password: str

    class Config:
        from_attributes = True
