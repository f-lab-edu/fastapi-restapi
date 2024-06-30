from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
# 파일 내의 동일한 디렉토리에 위치 그래서 마지막 부분이 ./app.db

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)  # SQLAlchemy 엔진생성 , engine은 나중에 다른곳에 사용
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# class 인스턴스 생성시, SessionLocal이 인스턴스가 실제 DB 세션이됨

Base = declarative_base()
# 이 클래스를 상속해서 각 DB 모델 또는 (ORM모델) 생성
