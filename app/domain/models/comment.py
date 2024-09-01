from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.domain.models.post import Post
from app.domain.models.user import User


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(String(255), ForeignKey("users.userid"), nullable=False)
    post_id = Column(
        Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    content = Column(Text, nullable=False)  # 내용 필드 필수로 설정, 인덱스 제거
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
