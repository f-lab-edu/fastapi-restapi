# conftest.py
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app  # FastAPI 인스턴스

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ENV"] = "development"  # 테스트 환경을 위한 ENV 설정
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 테스트를 위한 데이터베이스 세션 fixture
@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# FastAPI의 의존성 주입을 위한 fixture
@pytest.fixture(scope="module")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# 유저 인증용 토큰 생성을 위한 fixture
@pytest.fixture
def auth_headers(client):
    user_data = {
        "username": "testuser",
        "password": "testpassword",
        "nickname": "tester",
    }
    client.post("/users/", json=user_data)  # 테스트용 사용자 생성
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpassword"},
    )
    token = response.json().get("session_id")
    headers = {"Cookie": f"session_id={token}"}
    return headers
