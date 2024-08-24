from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


from passlib.hash import bcrypt

# 예시 비밀번호 해시화 및 비교
hashed_password = bcrypt.hash("Qwer1234")
print(hashed_password)

# 비교
if bcrypt.verify("Qwer1234", hashed_password):
    print("비밀번호 일치")
else:
    print("비밀번호 불일치")
