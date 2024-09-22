from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.utils import get_password_hash, verify_password
from app.domain.models.user import Role, User
from app.domain.schemas.user import UserCreate, UserInDB, UserRead, UserUpdate


class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="이미 존재하는 사용자 ID입니다.")


class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, user_create: UserCreate) -> UserRead:
        existing_user = (
            self.db.query(User).filter(User.userid == user_create.userid).first()
        )

        if existing_user:
            raise UserAlreadyExistsException()

        hashed_password = get_password_hash(user_create.password)
        user = User(
            userid=user_create.userid,
            nickname=user_create.nickname,
            hashed_password=hashed_password,
            role=user_create.role,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return UserRead.model_validate(user)

    def authenticate_user(self, userid: str, password: str) -> Optional[UserInDB]:
        user = self.db.query(User).filter(User.userid == userid).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return UserInDB.from_orm(user)

    def get(self, userid: str) -> Optional[UserInDB]:
        user = self.db.query(User).filter(User.userid == userid).first()
        if user:
            return UserInDB.from_orm(user)
        return None

    def get_by_userid(self, userid: str) -> Optional[UserInDB]:
        # 여기서 userid는 OAuth2PasswordRequestForm의 'username' 필드로 전송된 값이므로, 일관되게 사용해야 합니다.
        user = self.db.query(User).filter(User.userid == userid).first()
        if user:
            return UserInDB.from_orm(user)
        return None

    def get_multi(self, skip: int = 0, limit: int = 10) -> List[UserRead]:
        users = self.db.query(User).offset(skip).limit(limit).all()
        return [UserRead.from_orm(user) for user in users]

    def update(self, userid: str, user_update: UserUpdate) -> UserRead:
        # 유저가 있는지 확인
        user = self.db.query(User).filter(User.userid == userid).first()
        if not user:
            raise ValueError("유저가 없습니다.")
        if user_update.password:
            user.hashed_password = get_password_hash(user_update.password)
        update_data = user_update.dict(
            exclude_unset=True, exclude={"password"}
        )  # 'password' 필드 제외
        for key, value in update_data.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)

        return UserRead.from_orm(user)

    def delete(self, userid: str):
        user = self.db.query(User).filter(User.userid == userid).first()
        if user:
            self.db.delete(user)
            self.db.commit()
        else:
            raise ValueError("유저가 없습니다.")

    def delete_by_userid(self, userid: str):
        user = self.db.query(User).filter(User.userid == userid).first()
        if user:
            self.db.delete(user)
            self.db.commit()
        else:
            raise ValueError("유저가 없습니다.")
