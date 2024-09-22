from fastapi import FastAPI

from app.api.endpoints import router
from app.database import (
    Base,
    get_db,  # `engine` 대신 `get_engine`만 가져옴
    get_engine,
    lifespan,
)

app = FastAPI(lifespan=lifespan)


# 데이터베이스 초기화 코드 (필요 시 사용)
def initialize_database():
    engine = get_engine()  # 필요한 시점에 엔진을 생성
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


initialize_database()  # 애플리케이션 시작 시 데이터베이스 초기화

app.include_router(router)
