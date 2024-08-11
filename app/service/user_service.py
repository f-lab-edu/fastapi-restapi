from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.utils import get_password_hash, verify_password
from app.domain.models.user import Role, User
from app.domain.schemas.user import UserCreate, UserInDB, UserRead, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_create: UserCreate) -> UserRead:
        user = User(
            nickname=user_create.nickname,
            hashed_password=user_create.password,
            role=user_create.role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserRead.from_orm(user)

    def authenticate_user(self, nickname: str, password: str) -> Optional[UserInDB]:
        user = self.db.query(User).filter(User.nickname == nickname).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return UserInDB.from_orm(user)

    def get(self, user_id: int) -> Optional[UserInDB]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            return UserInDB.from_orm(user)
        return None

    def get_by_nickname(self, nickname: str) -> Optional[UserInDB]:
        user = self.db.query(User).filter(User.nickname == nickname).first()
        if user:
            return UserInDB.from_orm(user)
        return None

    def get_multi(self, skip: int = 0, limit: int = 10) -> List[UserRead]:
        users = self.db.query(User).offset(skip).limit(limit).all()
        return [UserRead.from_orm(user) for user in users]

    def update(self, user_id: int, user_update: UserUpdate) -> UserRead:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("유저가 없습니다.")
        if user_update.password:
            user.hashed_password = get_password_hash(user_update.password)
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return UserRead.from_orm(user)

    def delete(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            self.db.delete(user)
            self.db.commit()
        else:
            raise ValueError("유저가 없습니다.")
