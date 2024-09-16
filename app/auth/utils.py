import logging

from passlib.context import CryptContext
from passlib.hash import bcrypt

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

# 패스워드 암호화 및 검증을 위한 CryptContext 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# 예시 비밀번호 해시화 및 비교
hashed_password = bcrypt.hash("Qwer1234")
logger.info(f"Hashed Password: {hashed_password}")

# 비교
if bcrypt.verify("Qwer1234", hashed_password):
    logger.info("비밀번호 일치")
else:
    logger.warning("비밀번호 불일치")
