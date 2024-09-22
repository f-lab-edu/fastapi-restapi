# TODO: improt 문 순서

import pytest  # pytest 사용을 위해 import
from fastapi.testclient import TestClient  # FastAPI의 TestClient 사용
from sqlalchemy.orm import Session  # 세션 사용 시 필요

from app.auth.dependencies import get_current_user
from app.domain.models.post import Post
from app.domain.models.user import User
from app.domain.schemas.post import PostCreate
from app.service.post_service import PostService
from app.service.user_service import UserCreate, UserService
from app.domain.schemas.post import PostCreate
from app.test.conftest import db_session


# 유저 생성 성공 및 삭제
def test_create_user_success(client, db_session):
    # given - 사용자 데이터를 준비
    user_data = {
        "userid": "testuser123",
        "password": "Testpassword1234",
        "role": "MEMBER",
        "nickname": "tester",
    }

    # when - 사용자를 생성하는 POST 요청
    response = client.post("/users/", json=user_data)
    response_json = response.json()

    # then - 생성된 사용자 id 값을 활용해 DB에서 row를 가져옴
    created_user_id = response_json["id"]  # POST 응답에서 받은 id
    created_user = db_session.query(User).filter(User.id == created_user_id).first()

    all_user_data = (
        created_user.__dict__
    )  # SQLAlchemy 객체의 모든 데이터를 딕셔너리로 변환

    # 출력해보거나 특정 검증 수행
    assert response.status_code == 200
    print(all_user_data)  # 모든 필드 출력
    assert created_user is not None
    assert created_user.id == created_user_id  # id 일치 확인


# TODO: DB에 row가 들어갔는지 + 값은 잘 맞는지 확인하기
# TODO: 아래처럼 테스트 케이스 함수 이름 구체적으로 적기
# TODO: 실패할 수 있는 다른 경우도 생각해보기
def test_create_user_failure_when_user_already_exist(client):
    # given
    user_data = {
        "userid": "testuser123",  # 필수 필드
        "password": "Testpassword1234",  # 필수 필드
        "role": "MEMBER",  # 필수 필드
        "nickname": "tester",  # 필수 필드
    }

    # when
    response_first = client.post("/users/", json=user_data)

    # then
    assert response_first.status_code == 200  # 첫 번째 생성은 성공해야 함

    # 중복된 사용자를 다시 생성하는 요청
    response_second = client.post("/users/", json=user_data)

    # 중복된 사용자의 경우 409 Conflict 상태 코드를 기대
    assert response_second.status_code == 409
    assert "detail" in response_second.json()
    assert (
        response_second.json()["detail"] == "이미 존재하는 사용자 ID 또는 닉네임입니다."
    )


# 로그인 성공 및 실패
def test_login_success(client, db_session, mock_session_store):
    # 사용자 생성 먼저 진행
    # given
    user_service = UserService(db_session)
    user_data = UserCreate(
        userid="testuser123",
        password="Testpassword1234",
        role="MEMBER",
        nickname="tester",
    )
    user_service.create_user(user_data)

    # 로그인 요청
    # when
    login_data = {"username": "testuser123", "password": "Testpassword1234"}
    response = client.post("/login", data=login_data)

    assert response.status_code == 200
    assert "session_id" in response.json()

    # 세션 저장소에서 세션이 올바르게 생성되었는지 확인
    # then
    session_id = response.json()["session_id"]
    session_data = mock_session_store.get_session(session_id)
    assert session_data["userid"] == "testuser123"


def test_login_failure_wrong_password(client, db_session, mock_session_store):
    # 사용자 생성 먼저 진행
    user_service = UserService(db_session)
    user_data = UserCreate(
        userid="testuser123",
        password="Testpassword1234",  # 올바른 비밀번호로 사용자 생성
        role="MEMBER",
        nickname="tester",
    )
    user_service.create_user(user_data)

    # 잘못된 비밀번호로 로그인 요청
    login_data = {
        "username": "testuser123",
        "password": "WrongPassword",  # 잘못된 비밀번호 입력
    }
    response = client.post("/login", data=login_data)

    # 응답 검사
    assert response.status_code == 401  # 401 Unauthorized 상태 코드 확인
    assert (
        response.json()["detail"] == "잘못된 사용자 이름 또는 비밀번호"
    )  # 응답 메시지 확인

    # 세션이 생성되지 않았는지 확인 (세션이 없어야 함)
    session_data = mock_session_store.get_session("some_invalid_session_id")
    assert session_data is None  # 세션이 존재하지 않아야 함


# 게시글 작성 성공 및 실패
@pytest.fixture
def authenticated_user(db_session):
    """테스트용으로 인증된 사용자를 생성하는 fixture"""
    test_user = User(
        userid="testuser",
        nickname="tester",
        hashed_password="hashedpassword123",
        role="MEMBER",
    )
    db_session.add(test_user)
    db_session.commit()
    return test_user


def test_create_post_success(
    client: TestClient, db_session: Session, authenticated_user
):
    # 게시글 데이터를 준비
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
    }

    # 가짜 로그인 처리 (현재 인증된 사용자)
    def mock_get_current_user():
        return authenticated_user

    client.app.dependency_overrides[get_current_user] = mock_get_current_user

    # 게시글 생성 요청
    response = client.post("/posts/", json=post_data)

    # 응답 코드 확인
    assert response.status_code == 200
    response_data = response.json()

    # 생성된 게시글 ID를 추출
    created_post_id = response_data["id"]

    # DB에서 해당 게시글을 id로 직접 조회
    created_post = db_session.query(Post).filter(Post.id == created_post_id).first()

    # 게시글의 모든 필드를 출력 (디버그용)
    print(
        created_post.__dict__
    )  # 모든 필드 출력 (SQLAlchemy 객체를 dict로 변환하여 출력)

    # DB에서 가져온 데이터와 응답 데이터를 비교하여 검증
    assert created_post.title == post_data["title"]
    assert created_post.content == post_data["content"]
    assert created_post.author_id == authenticated_user.userid

    # 응답으로 돌아온 데이터와 DB에 저장된 데이터가 일치하는지 확인
    assert response_data["title"] == created_post.title
    assert response_data["content"] == created_post.content
    assert response_data["author"]["userid"] == authenticated_user.userid


def test_create_post_failure_missing_title(
    client: TestClient, db_session: Session, authenticated_user
):
    # 제목이 없는 게시글 생성 시도
    post_data = {
        "content": "This is a test post content.",
    }

    # 가짜 로그인 처리 (현재 인증된 사용자)
    def mock_get_current_user():
        return authenticated_user

    # 의존성 오버라이드 설정
    # TODO: 모킹을 쓰면 페이크 객체보다 뭐가 더 좋고 안좋을까? (그 반대는?)
    # TOOD: 그 밖에 테스트 더블은 뭐가 있을까? 장단점은 뭔지? 그리고 언제 쓰면 좋은지?
    client.app.dependency_overrides[get_current_user] = mock_get_current_user

    # 게시글 생성 요청 (제목 누락)
    response = client.post("/posts/", json=post_data)

    assert response.status_code == 422  # 필수 필드 누락으로 인한 검증 실패
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["loc"] == ["body", "title"]


# def test_create_post_success(client: TestClient, db_session: Session, authenticated_user):
#     # 게시글 데이터를 준비
#     post_data = {
#         "title": "Test Post",
#         "content": "This is a test post content.",
#     }
#
#     # 가짜 로그인 처리 (현재 인증된 사용자)
#     def mock_get_current_user():
#         return authenticated_user
#
#     client.app.dependency_overrides[get_current_user] = mock_get_current_user
#
#     # 게시글 생성 요청
#     response = client.post("/posts/", json=post_data)
#
#     # 응답 코드 확인
#     assert response.status_code == 200
#     response_data = response.json()
#
#     # 생성된 게시글 ID를 추출
#     created_post_id = response_data["id"]
#
#     # 커밋 확인
#     db_session.commit()
#
#     # DB에서 해당 게시글을 id로 직접 조회
#     created_post = db_session.query(Post).filter(Post.id == created_post_id).first()
#
#     # 게시글의 모든 필드를 출력 (디버그용)
#     assert created_post is not None, "The post should exist in the database after creation."
#     print(created_post.__dict__)  # 모든 필드 출력 (SQLAlchemy 객체를 dict로 변환하여 출력)
#
#     # 생성된 게시글의 필드 값 검증
#     assert created_post.title == post_data["title"]
#     assert created_post.content == post_data["content"]
#     assert created_post.author_id == authenticated_user.userid


def test_read_post_not_found(client):
    # given - 존재하지 않는 게시글 ID
    non_existing_post_id = 9999

    # when - 게시글 조회 API 호출
    response = client.get(f"/posts/{non_existing_post_id}")

    # then - 404 Not Found 상태 코드와 적절한 오류 메시지 확인
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "게시글이 없습니다."
