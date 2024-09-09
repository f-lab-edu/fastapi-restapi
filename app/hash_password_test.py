import logging

from app.auth.utils import get_password_hash

# 로거 설정
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_password_hash():
    password = "TestPassword123"
    hashed_password = get_password_hash(password)
    logger.debug(f"Original password: {password}")
    logger.info(f"Hashed password: {hashed_password}")


if __name__ == "__main__":
    test_password_hash()
