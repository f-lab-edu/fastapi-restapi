from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:password@db:3306/mydatabase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.on_event("startup")
def on_startup():
    print("Database engine connected.")


@app.on_event("shutdown")
def on_shutdown():
    engine.dispose()
    print("Database engine disposed.")


@app.on_event("startup")
def on_startup():
    # 데이터베이스 연결 확인용 로그
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT DATABASE();")
            print("Database connection successful:", result.fetchone())
    except SQLAlchemyError as e:
        print("Database connection failed:", e)
