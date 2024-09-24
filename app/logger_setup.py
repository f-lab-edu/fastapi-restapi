import logging
import os

from dotenv import load_dotenv

load_dotenv(".env")

log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
log_format = os.getenv(
    "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, log_level, logging.DEBUG))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(log_format)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)
