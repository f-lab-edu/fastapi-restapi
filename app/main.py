# app/main.py
from fastapi import FastAPI

#
from app.api.endpoints import router as api_router
from app.api.endpoints import router as auth_router

# from app.auth.auth import router as auth_router
from app.database import Base, engine

app = FastAPI()

app.include_router(api_router, prefix="/api", tags=["api"])

# 기존 테이블 삭제
Base.metadata.drop_all(bind=engine)
# 새로운 테이블 생성
Base.metadata.create_all(bind=engine)
