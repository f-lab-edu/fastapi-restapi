# conftest.py
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from testcontainers.mysql import MySqlContainer

from app.database import Base, get_db, get_engine
from app.session_store import DBSessionStore, get_session_store  # DBSessionStore 임포트


# `Testcontainers`를 사용하여 MySQL 컨테이너 생성
@pytest.fixture(scope="session")
def mysql_container():
    with MySqlContainer("mysql:8.0") as mysql:
        mysql.start()  # 컨테이너 시작
        yield mysql  # 컨테이너 URL을 반환하여 테스트에서 사용 가능


# 데이터베이스 세션을 설정하는 fixture
@pytest.fixture(scope="session")
def db_engine(mysql_container):
    # 환경 변수를 통해 SQLAlchemy 엔진이 Testcontainers의 MySQL URL을 사용하도록 설정
    os.environ["DATABASE_URL"] = mysql_container.get_connection_url()
    engine = get_engine()  # `get_engine()`을 사용해 엔진을 생성
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 데이터베이스 초기화
    Base.metadata.create_all(bind=engine)

    yield TestingSessionLocal  # sessionmaker 객체를 반환

    # 테스트 후 정리 작업: 데이터베이스 테이블 제거
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """세션 생성 및 종료"""
    db = db_engine()  # sessionmaker에서 세션 생성
    Base.metadata.drop_all(bind=db.get_bind())  # 테이블 삭제
    Base.metadata.create_all(bind=db.get_bind())  # 테이블 생성
    db = db_engine()  # sessionmaker에서 세션 생성
    try:
        yield db
    finally:
        db.close()


# Mock session store fixture 추가
@pytest.fixture(scope="function")
def mock_session_store(db_session):
    # DBSessionStore의 인스턴스를 db_session과 함께 생성
    store = DBSessionStore(db=db_session)
    return store


# FastAPI 애플리케이션을 가져오기 전에 환경 변수를 설정한 후 import
@pytest.fixture(scope="session")
def app(db_engine):
    # FastAPI 애플리케이션 import는 환경 변수 설정 후에 해야 함
    from app.main import app  # 환경 변수 설정 후에 가져오기

    return app


# FastAPI 테스트 클라이언트 설정
@pytest.fixture(scope="function")
def client(app, db_engine, mock_session_store):
    # FastAPI 의존성 오버라이드 설정
    def override_get_db():
        db = db_engine()  # sessionmaker에서 세션 생성
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # 세션 저장소 의존성 오버라이드
    app.dependency_overrides[get_session_store] = lambda: mock_session_store

    # 테스트 클라이언트 생성
    with TestClient(app) as c:
        yield c
