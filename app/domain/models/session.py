from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    session_id = Column(String(36), primary_key=True, index=True)
    data = Column(String(255))
    expires_at = Column(DateTime)

    # `user_id`는 `users` 테이블의 `id`를 참조하는 외래 키입니다.
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )  # 각 User당 하나의 Session만 허용

    # User와의 1:1 관계 설정
    user = relationship("User", back_populates="session")
