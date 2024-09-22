import os


def test_env_variable_loaded():
    # 환경 변수가 잘 로드되었는지 확인
    db_url = os.getenv("DATABASE_URL")
    assert db_url is not None, "DATABASE_URL 환경 변수가 로드되지 않았습니다."
    print(f"DATABASE_URL: {db_url}")
