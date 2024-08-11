# app/domain/models/post.py
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from app.database import Base
from app.domain.models.user import User


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, index=True)
    content = Column(Text, index=True)
    author = relationship("User")
    created_at = Column(DateTime, default=datetime.utcnow)
