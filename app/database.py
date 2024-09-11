import os
from contextlib import asynccontextmanager

import sqlalchemy
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL", "mysql+pymysql://exampleuser:examplepassword@localhost/exampledb"
)
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI 애플리케이션 생성
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Database engine 연결.")
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT DATABASE();")
            print("Database 연결 성공:", result.fetchone())
    except SQLAlchemyError as e:
        print("Database 연결 실패:", e)

    yield

    engine.dispose()
    print("Database engine 종료.")


app = FastAPI(lifespan=lifespan)
