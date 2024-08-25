import uuid
from datetime import datetime, timedelta


# 세션 관리 클래스 정의
class SessionStore:
    def __init__(self):
        self.store = {}

    def create_session(self, data: dict, expires_in: timedelta):
        session_id = str(uuid.uuid4())
        expiration_time = datetime.utcnow() + expires_in
        self.store[session_id] = {"data": data, "expires_at": expiration_time}
        return session_id

    def get_session(self, session_id: str):
        session = self.store.get(session_id)
        if session and session["expires_at"] > datetime.utcnow():
            return session["data"]
        return None

    def delete_session(self, session_id: str):
        if session_id in self.store:
            del self.store[session_id]


# 인스턴스 생성
session_store = SessionStore()
