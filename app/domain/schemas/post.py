from datetime import datetime

from pydantic import BaseModel


class PostBase(BaseModel):
    author: str
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostRead(PostBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PostUpdate(BaseModel):
    author: str = None
    title: str = None
    content: str = None
