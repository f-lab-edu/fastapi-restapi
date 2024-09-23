import json  # JSON 직렬화/역직렬화 모듈 추가
import uuid
from datetime import datetime, timedelta

from fastapi import Depends
from sqlalchemy.orm import Session  # Session 임포트

from app.database import get_db  # DB 종속성 가져오기
from app.domain.models.session import \
    SessionModel  # SessionModel이 정의된 파일로부터 임포트


class DBSessionStore:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, data: dict, expires_in: timedelta):
        session_id = str(uuid.uuid4())
        expiration_time = datetime.utcnow() + expires_in
        session_data = json.dumps(data)  # 데이터를 JSON으로 직렬화하여 저장

        # 세션 생성 및 DB에 저장
        new_session = SessionModel(
            session_id=session_id, data=session_data, expires_at=expiration_time
        )
        try:
            self.db.add(new_session)
            self.db.commit()
        except Exception as e:
            self.db.rollback()  # 에러 발생 시 롤백
            raise e

        return session_id

    def get_session(self, session_id: str):
        # DB에서 세션 조회
        session = (
            self.db.query(SessionModel)
            .filter(SessionModel.session_id == session_id)
            .first()
        )
        if session and session.expires_at > datetime.utcnow():
            return json.loads(session.data)  # JSON 문자열을 원래 데이터 형식으로 변환
        return None

    def delete_session(self, session_id: str):
        # DB에서 세션 삭제
        session = (
            self.db.query(SessionModel)
            .filter(SessionModel.session_id == session_id)
            .first()
        )
        if session:
            try:
                self.db.delete(session)
                self.db.commit()
            except Exception as e:
                self.db.rollback()  # 에러 발생 시 롤백
                raise e


# DBSessionStore 인스턴스 생성 (의존성 주입에서 사용할 수 있도록)
def get_session_store(db: Session = Depends(get_db)):
    return DBSessionStore(db)
