# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from fastapi import FastAPI

Base = declarative_base()

def get_engine():
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@db:3306/mydatabase")
    return create_engine(SQLALCHEMY_DATABASE_URL, connect_args={})

def get_session_local():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Lifespan 컨텍스트 관리자 정의
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("애플리케이션이 시작되었습니다.")
    try:
        yield
    finally:
        print("애플리케이션이 종료되었습니다.")
        # 필요 시 다른 정리 작업 수행
