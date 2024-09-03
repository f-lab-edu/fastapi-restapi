import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://root:password@db:3306/mydatabase"
)

# SQLite 데이터베이스일 경우 특수한 연결 인자 설정
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

# 세션 로컬 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 데이터베이스 세션을 가져오는 종속성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI 애플리케이션 생성
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 애플리케이션 시작 시 작업
    print("Database engine connected.")

    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT DATABASE();")
            print("Database connection successful:", result.fetchone())
    except SQLAlchemyError as e:
        print("Database connection failed:", e)

    yield

    # 애플리케이션 종료 시 작업
    engine.dispose()
    print("Database engine disposed.")


app = FastAPI(lifespan=lifespan)
