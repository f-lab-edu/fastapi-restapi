from app.auth.utils import get_password_hash


def test_password_hash():
    password = "TestPassword123"
    hashed_password = get_password_hash(password)
    print(f"Original password: {password}")
    print(f"Hashed password: {hashed_password}")


if __name__ == "__main__":
    test_password_hash()
