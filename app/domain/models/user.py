import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class Role(enum.Enum):
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    userid = Column(String(36), unique=True, index=True, nullable=False)
    nickname = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(Role), default=Role.MEMBER, nullable=False)
    created_at = Column(
        DateTime, default=func.now(), nullable=False, server_default=func.now()
    )

    comments = relationship(
        "Comment", back_populates="author", cascade="all, delete-orphan"
    )
