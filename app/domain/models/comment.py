# app/domain/models/comment.py
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app import Base
from app.domain.models.post import Post
from app.domain.models.user import User


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    content = Column(Text, index=True)
    author = relationship("User")
    post = relationship("Post")
    created_at = Column(DateTime, default=datetime.utcnow)
