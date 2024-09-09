import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 로거 설정
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Database engine 연결 시도 중...")
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT DATABASE();")
            logger.info("Database 연결 성공: %s", result.fetchone())
    except SQLAlchemyError as e:
        logger.error("Database 연결 실패: %s", e)

    yield
    engine.dispose()
    logger.info("Database engine 종료.")


app = FastAPI(lifespan=lifespan)
