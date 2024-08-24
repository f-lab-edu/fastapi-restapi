# app/main.py
from fastapi import FastAPI

#
from app.api.endpoints import router as api_router
from app.api.endpoints import router as auth_router
# from app.auth.auth import router as auth_router
from app.database import Base, engine

app = FastAPI()


# app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(api_router, prefix="/api", tags=["api"])
# 인증 및 보호된 라우터 등록
# api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
# app.include_router(protected.router, prefix="/protected", tags=["protected"])

# main 실행 코드
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# 기존 테이블 삭제
Base.metadata.drop_all(bind=engine)
# 새로운 테이블 생성
Base.metadata.create_all(bind=engine)
