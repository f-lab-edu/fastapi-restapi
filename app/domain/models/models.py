from sqlalchemy import DATETIME, Column, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class Post(Base):
    __tablename__ = "posts"
    id = Column(
        Integer, primary_key=True, index=True
    )  # 기본키 설정으로 중복값을 가질 수 없게
    author = Column(String, index=True)
    title = Column(String, index=True)
    content = Column(Text, index=True)
    created_at = Column(
        DATETIME(timezone=True), server_default=func.now(), nullable=False
    )
