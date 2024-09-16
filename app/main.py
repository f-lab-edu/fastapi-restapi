
from fastapi import FastAPI

from app.api.endpoints import router
from app.database import Base, engine, get_db

app = FastAPI()

app.include_router(router, prefix="/api", tags=["api"])

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
