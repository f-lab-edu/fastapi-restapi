from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db  # 세션 관리를 위한 DB 의존성 가져오기
from app.domain.schemas.user import UserInDB
from app.session_store import DBSessionStore  # DBSessionStore 사용


# DBSessionStore 인스턴스 생성
def get_db_session_store(db: Session = Depends(get_db)):
    return DBSessionStore(db)


def get_current_user(
    session_id: str = Cookie(None),
    session_store: DBSessionStore = Depends(
        get_db_session_store
    ),  # DBSessionStore 사용
) -> UserInDB:
    # 쿠키에 세션 ID가 없을 경우
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # 401로 수정
            detail="세션 ID가 없거나 유효하지 않습니다.",
        )

    # 세션 스토어에서 세션 데이터 가져오기
    session_data = session_store.get_session(session_id)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # 401로 수정
            detail="세션을 찾을 수 없거나 만료되었습니다.",
        )

    # session_data에서 유저 정보를 UserInDB로 변환
    return UserInDB(**session_data)
