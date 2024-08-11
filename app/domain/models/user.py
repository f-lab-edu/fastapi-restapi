# app/domain/models/user.py
import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String

from app.database import Base


class Role(enum.Enum):
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(Role), default=Role.MEMBER)
    created_at = Column(DateTime, default=datetime.utcnow)
