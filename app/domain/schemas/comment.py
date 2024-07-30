from datetime import datetime

from pydantic import BaseModel


class CommentBase(BaseModel):
    author_id: int
    post_id: int
    content: str


class CommentCreate(CommentBase):
    pass


class CommentRead(CommentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommentUpdate(BaseModel):
    content: str = None
