import uuid
from datetime import datetime, timedelta
from typing import Optional


class InMemorySessionStore:
    def __init__(self):
        self.sessions = {}

    def create_session(
        self, user_data: dict, expires_in: timedelta = timedelta(days=1)
    ) -> str:
        session_id = str(uuid.uuid4())
        expiry_time = datetime.utcnow() + expires_in
        self.sessions[session_id] = {"data": user_data, "expires_at": expiry_time}
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        session = self.sessions.get(session_id)
        if session:
            # 세션 만료 확인
            if session["expires_at"] > datetime.utcnow():
                return session["data"]
            else:
                # 세션이 만료되었으면 삭제
                self.delete_session(session_id)
        return None

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]


# 전역 인스턴스 생성
session_store = InMemorySessionStore()
