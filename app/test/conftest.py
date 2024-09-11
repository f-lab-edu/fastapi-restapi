# test_conftest.py
import os

import pytest
import sqlalchemy as sa
from starlette.testclient import TestClient
from testcontainers.mysql import MySqlContainer

from app.main import app


@pytest.fixture(scope="module")
def mysql_container():
    container = MySqlContainer("mysql:8.0.33")  # 사용할 MySQL 이미지와 버전
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope="module")
def engine(mysql_container):
    # Testcontainers에서 받은 데이터베이스 연결 URL을 설정합니다.
    connection_string = mysql_container.get_connection_url()
    engine = sa.create_engine(connection_string)
    return engine


# 테스트에서 사용할 데이터베이스 URL을 환경 변수로 설정합니다.
@pytest.fixture(scope="module")
def set_environment_variables(mysql_container):
    os.environ["DATABASE_URL"] = mysql_container.get_connection_url()


@pytest.fixture
def client():
    return TestClient(app)
