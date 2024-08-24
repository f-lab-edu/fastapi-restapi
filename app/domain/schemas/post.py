from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.domain.schemas.user import UserRead


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostRead(PostBase):
    id: int
    author: UserRead
    created_at: datetime

    class Config:
        from_attributes = True


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
