from datetime import datetime

from pydantic import BaseModel

from app.domain.schemas.user import UserRead


class PostBase(BaseModel):
    author: str
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
    author: str = None
    title: str = None
    content: str = None
