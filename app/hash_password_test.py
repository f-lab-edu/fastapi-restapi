import logging

from app.auth.utils import get_password_hash

# 로거 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 로그 레벨 설정

# 콘솔 출력 핸들러 생성
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 로그 포맷터 생성
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)

# 로거에 핸들러 추가
logger.addHandler(console_handler)


def test_password_hash():
    password = "TestPassword123"
    hashed_password = get_password_hash(password)
    logger.info(f"Original password: {password}")
    logger.info(f"Hashed password: {hashed_password}")


if __name__ == "__main__":
    test_password_hash()
