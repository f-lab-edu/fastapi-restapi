# database.py
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.logger_setup import logger

Base = declarative_base()


def get_engine():
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:password@db:3306/mydatabase"
    )
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("애플리케이션이 시작되었습니다.")
    try:
        yield
    finally:
        logger.info("애플리케이션이 종료되었습니다.")
