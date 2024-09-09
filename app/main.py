import os

from fastapi import FastAPI

from app.api.endpoints import router as api_router
from app.database import Base, engine, get_db

app = FastAPI()

app.include_router(api_router, prefix="/api", tags=["api"])

env = os.getenv("ENV", "production")

if env == "development":
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
else:
    print("Running in production mode; no automatic table creation or deletion.")
