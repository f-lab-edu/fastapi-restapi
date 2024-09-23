from passlib.context import CryptContext
from passlib.hash import bcrypt

from app.logger_setup import logger

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
