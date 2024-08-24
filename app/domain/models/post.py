from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import joinedload, relationship

from app.database import Base
from app.domain.models.user import User


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(
        String(36), ForeignKey("users.userid"), nullable=False
    )  # User 모델의 userid 필드와 연결
    title = Column(
        String(255), index=True, nullable=False
    )  # 제목 필드, nullable=False 추가
    content = Column(Text, nullable=False)  # 내용 필드, nullable=False 추가
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    author = relationship("User", back_populates="posts")
    comments = relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )
