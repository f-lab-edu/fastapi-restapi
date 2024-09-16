from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.utils import get_password_hash, verify_password
from app.domain.models.user import Role, User
from app.domain.schemas.user import UserCreate, UserInDB, UserRead, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_create: UserCreate) -> UserRead:
        # 먼저 중복된 userid 또는 nickname이 있는지 확인
        existing_user = (
            self.db.query(User)
            .filter(
                (User.userid == user_create.userid)
                | (User.nickname == user_create.nickname)
            )
            .first()
        )

        if existing_user:
            raise ValueError("이미 존재하는 사용자 ID 또는 닉네임입니다.")

            # 비밀번호 해시화
        hashed_password = get_password_hash(user_create.password)

        # 사용자 생성 및 데이터베이스에 저장
        user = User(
            userid=user_create.userid,
            nickname=user_create.nickname,
            hashed_password=hashed_password,
            role=user_create.role,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return UserRead.from_orm(user)

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
        user = self.db.query(User).filter(User.userid == userid).first()
        if not user:
            raise ValueError("유저가 없습니다.")
        if user_update.password:
            user.hashed_password = get_password_hash(user_update.password)
        for key, value in user_update.dict(exclude_unset=True).items():
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
