from fastapi import Cookie, Depends, HTTPException

from app.domain.schemas.user import UserInDB
from app.session_store import session_store


def get_current_user(session_id: str = Cookie(None)) -> UserInDB:
    session_data = session_store.get_session(session_id)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="세션을 찾을 수 없거나 만료되었습니다.",
        )

    # session_data에서 유저 정보를 UserInDB로 변환
    return UserInDB(**session_data)
