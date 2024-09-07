import logging
from passlib.context import CryptContext


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    is_valid = pwd_context.verify(plain_password, hashed_password)
    if is_valid:
        logger.debug("비밀번호가 일치합니다.")
    else:
        logger.debug("비밀번호가 일치하지 않습니다.")
    return is_valid

def get_password_hash(password):
    hashed = pwd_context.hash(password)
    logger.debug(f"해시된 비밀번호: {hashed}")
    return hashed

hashed_password = get_password_hash("Qwer1234")

if verify_password("Qwer1234", hashed_password):
    logger.info("비밀번호가 일치합니다.")
else:
    logger.info("비밀번호가 일치하지 않습니다.")
