from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PostBase(BaseModel):
    author: str
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    author: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None


class PostRead(PostBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
