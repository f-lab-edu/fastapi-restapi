import logging
import os

from fastapi import FastAPI

from app.api.endpoints import router as api_router
from app.database import Base, engine, get_db

# 로거 설정
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(api_router, prefix="/api", tags=["api"])

env = os.getenv("ENV", "production")

if env == "development":
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)
else:
    logger.info("Running in production mode; no automatic table creation or deletion.")
