from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CommentBase(BaseModel):
    author_id: int
    post_id: int
    content: str


class CommentCreate(CommentBase):
    pass


class CommentRead(BaseModel):
    id: int
    author_id: int
    post_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class CommentUpdate(BaseModel):
    content: Optional[str] = None
