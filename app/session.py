from datetime import datetime, timedelta
from typing import Dict


class Session:
    def __init__(self, session_id: str, expires: datetime):
        self.session_id = session_id
        self.expires = expires


class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(self, session_id: str):
        expires = datetime.utcnow() + timedelta(days=1)
        self.sessions[session_id] = Session(session_id, expires)

    def get_session(self, session_id: str) -> Session:
        session = self.sessions.get(session_id)
        if session and session.expires > datetime.utcnow():
            return session
        else:
            self.sessions.pop(session_id, None)
            return None

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def refresh_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id].expires = datetime.utcnow() + timedelta(days=1)
        else:
            self.create_session(session_id)


# 인스턴스 생성
session_store = SessionStore()
