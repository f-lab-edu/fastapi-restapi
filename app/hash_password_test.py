from app.auth.utils import get_password_hash
from app.logger_setup import logger


def test_password_hash():
    password = "TestPassword123"
    hashed_password = get_password_hash(password)
    logger.info(f"Original password: {password}")
    logger.info(f"Hashed password: {hashed_password}")


if __name__ == "__main__":
    test_password_hash()
