from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.utils import verify_password
from app.database import get_db
from app.service.user_service import UserService
from app.session_store import session_store

router = APIRouter()


@router.post("/token")
def login_for_session(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    response: Response = Response(),
):
    user_service = UserService(db)
    user = user_service.get_by_nickname(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # 세션 생성 후 쿠키에 저장 (1일 만료)
    session_id = session_store.create_session(
        {"username": user.nickname}, expires_in=timedelta(days=1)
    )
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    return {"message": "Login successful"}
