<<<<<<< HEAD
=======
# TODO: improt 문 순서

>>>>>>> ee5771430b0025a122ae61e2786cc1c8b222e56c
import pytest  # pytest 사용을 위해 import
from fastapi.testclient import TestClient  # FastAPI의 TestClient 사용
from sqlalchemy.orm import Session  # 세션 사용 시 필요
from app.test.conftest import db_session
from app.service.user_service import UserService, UserCreate
from app.domain.models.user import User
from app.domain.models.post import Post
from app.domain.schemas.post import PostCreate
from app.service.post_service import PostService
from app.auth.dependencies import get_current_user

<<<<<<< HEAD
# 유저 생성 성공 및 삭제
def test_create_user_success(client):
=======
# TODO: 나머지 엔드포인트들도 테스트 함수 모두 추가하기

# 유저 생성 성공 및 삭제
def test_create_user_success(client):
    # TODO: given / when / then 주석 추가하기
    # given
>>>>>>> ee5771430b0025a122ae61e2786cc1c8b222e56c
    user_data = {
        "userid": "testuser123",
        "password": "Testpassword1234",
        "role": "MEMBER",
        "nickname": "tester"
    }
<<<<<<< HEAD
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    response_json = response.json()

=======

    # when
    response = client.post("/users/", json=user_data)

    # then
    assert response.status_code == 200
    response_json = response.json()
>>>>>>> ee5771430b0025a122ae61e2786cc1c8b222e56c
    assert response_json["userid"] == "testuser123"
    assert response_json["nickname"] == "tester"
    assert "id" in response_json
    assert "created_at" in response_json

<<<<<<< HEAD
def test_create_user_failure(client):
=======
    # TODO: DB에 row가 들어갔는지 + 값은 잘 맞는지 확인하기

# TODO: 아래처럼 테스트 케이스 함수 이름 구체적으로 적기
# TODO: 실패할 수 있는 다른 경우도 생각해보기
def test_create_user_failure_when_user_already_exist(client):
>>>>>>> ee5771430b0025a122ae61e2786cc1c8b222e56c
    # 같은 사용자를 다시 생성하여 유니크 제약 조건 위반을 유발
    user_data = {
        "userid": "testuser123",  # 필수 필드
        "password": "Testpassword1234",  # 필수 필드
        "role": "MEMBER",  # 필수 필드
        "nickname": "tester"  # 필수 필드
    }

    # 첫 번째 요청으로 사용자를 생성
    response_first = client.post("/users/", json=user_data)
    assert response_first.status_code == 200  # 첫 번째 생성은 성공해야 함

    # 동일한 데이터를 다시 보내서 유니크 제약 조건을 위반
    response_second = client.post("/users/", json=user_data)

    # 응답 상태 코드가 400인지 확인 (중복된 사용자로 인해 실패해야 함)
<<<<<<< HEAD
=======
    # TODO: 409로 수정하기
>>>>>>> ee5771430b0025a122ae61e2786cc1c8b222e56c
    assert response_second.status_code == 400  # 중복 사용자로 인한 400 상태 코드 기대

    # 응답에 'detail' 필드가 있는지 확인 (에러 메시지 포함)
    assert "detail" in response_second.json()
    assert response_second.json()["detail"] == "이미 존재하는 사용자 ID 또는 닉네임입니다."


# 로그인 성공 및 실패
def test_login_success(client, db_session, mock_session_store):
    # 사용자 생성 먼저 진행
    user_service = UserService(db_session)
    user_data = UserCreate(
        userid="testuser123",
        password="Testpassword1234",
        role="MEMBER",
        nickname="tester"
    )
    user_service.create_user(user_data)

    # 로그인 요청
    login_data = {
        "username": "testuser123",
        "password": "Testpassword1234"
    }
    response = client.post("/login", data=login_data)

    assert response.status_code == 200
    assert "session_id" in response.json()

    # 세션 저장소에서 세션이 올바르게 생성되었는지 확인
    session_id = response.json()["session_id"]
    session_data = mock_session_store.get_session(session_id)  # get_session을 mock_session_store에서 호출
    assert session_data["userid"] == "testuser123"

def test_login_failure_wrong_password(client, db_session, mock_session_store):
    # 사용자 생성 먼저 진행
    user_service = UserService(db_session)
    user_data = UserCreate(
        userid="testuser123",
        password="Testpassword1234",  # 올바른 비밀번호로 사용자 생성
        role="MEMBER",
        nickname="tester"
    )
    user_service.create_user(user_data)

    # 잘못된 비밀번호로 로그인 요청
    login_data = {
        "username": "testuser123",
        "password": "WrongPassword"  # 잘못된 비밀번호 입력
    }
    response = client.post("/login", data=login_data)

    # 응답 검사
    assert response.status_code == 401  # 401 Unauthorized 상태 코드 확인
    assert response.json()["detail"] == "잘못된 사용자 이름 또는 비밀번호"  # 응답 메시지 확인

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
        role="MEMBER"
    )
    db_session.add(test_user)
    db_session.commit()
    return test_user


def test_create_post_success(client: TestClient, db_session: Session, authenticated_user):
    # 사용자 인증 및 게시글 생성 테스트
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
    }

    # 가짜 로그인 처리 (현재 인증된 사용자)
    def mock_get_current_user():
        return authenticated_user

    # 의존성 오버라이드 설정
    client.app.dependency_overrides[get_current_user] = mock_get_current_user

    # 게시글 생성 요청
    response = client.post("/posts/", json=post_data)

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["title"] == post_data["title"]
    assert response_data["content"] == post_data["content"]

    # 작성자 정보 확인: 작성자는 딕셔너리로 반환되므로, 작성자 필드에서 userid를 비교
    assert response_data["author"]["userid"] == authenticated_user.userid


def test_create_post_failure_missing_title(client: TestClient, db_session: Session, authenticated_user):
    # 제목이 없는 게시글 생성 시도
    post_data = {
        "content": "This is a test post content.",
    }

    # 가짜 로그인 처리 (현재 인증된 사용자)
    def mock_get_current_user():
        return authenticated_user

    # 의존성 오버라이드 설정
<<<<<<< HEAD
=======
    # TODO: 모킹을 쓰면 페이크 객체보다 뭐가 더 좋고 안좋을까? (그 반대는?)
    # TOOD: 그 밖에 테스트 더블은 뭐가 있을까? 장단점은 뭔지? 그리고 언제 쓰면 좋은지?
>>>>>>> ee5771430b0025a122ae61e2786cc1c8b222e56c
    client.app.dependency_overrides[get_current_user] = mock_get_current_user

    # 게시글 생성 요청 (제목 누락)
    response = client.post("/posts/", json=post_data)

    assert response.status_code == 422  # 필수 필드 누락으로 인한 검증 실패
    assert response.json()["detail"][0]["msg"] == "Field required"
    assert response.json()["detail"][0]["loc"] == ["body", "title"]


def test_create_post_failure_unauthenticated(client: TestClient):
    # 인증되지 않은 사용자가 게시글을 생성하려고 할 때
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
    }

    # 인증 없이 게시글 생성 요청
    response = client.post("/posts/", json=post_data, cookies=None)

    # 서버가 인증되지 않은 요청에 대해 올바르게 응답하는지 확인
    assert response.status_code == 401  # 인증되지 않은 사용자여야 함

