# TODO: improt 문 순서

import pytest  # pytest 사용을 위해 import
from fastapi.testclient import TestClient  # FastAPI의 TestClient 사용
from sqlalchemy.orm import Session  # 세션 사용 시 필요

from app.auth.dependencies import get_current_user
from app.auth.utils import get_password_hash, verify_password
from app.domain.models.comment import Comment
from app.domain.models.post import Post
from app.domain.models.user import User
from app.domain.schemas.post import PostCreate, PostUpdate
from app.service.post_service import PostService
from app.service.user_service import UserCreate, UserService
from app.test.conftest import authenticated_user, db_session


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

    all_user_data = created_user.__dict__
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
    assert response_second.json()["detail"] == "이미 존재하는 사용자 ID입니다."


# 로그인 성공 및 실패
def test_login_success(client, db_session, mock_session_store):
    # given
    user_service = UserService(db_session)
    user_data = UserCreate(
        userid="testuser123",
        password="Testpassword1234",
        role="MEMBER",
        nickname="tester",
    )
    user_service.create_user(user_data)

    # when
    login_data = {"username": "testuser123", "password": "Testpassword1234"}
    response = client.post("/login", data=login_data)

    assert response.status_code == 200
    assert "session_id" in response.json()

    # then
    session_id = response.json()["session_id"]
    session_data = mock_session_store.get_session(session_id)
    assert session_data["userid"] == "testuser123"


def test_login_failure_wrong_password(client, db_session, mock_session_store):
    # given
    user_service = UserService(db_session)
    user_data = UserCreate(
        userid="testuser123",
        password="Testpassword1234",  # 올바른 비밀번호로 사용자 생성
        role="MEMBER",
        nickname="tester",
    )
    user_service.create_user(user_data)

    # when
    login_data = {
        "username": "testuser123",
        "password": "WrongPassword",  # 잘못된 비밀번호 입력
    }
    response = client.post("/login", data=login_data)

    # then
    assert response.status_code == 401  # 401 Unauthorized 상태 코드 확인
    assert response.json()["detail"] == "잘못된 사용자 이름 또는 비밀번호"
    session_data = mock_session_store.get_session("잘못된 session_id")
    assert session_data is None


# 게시글 작성 성공 및 실패


def test_create_post_success(
    client: TestClient, db_session: Session, authenticated_user
):
    # 게시글 데이터를 준비
    # given
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
    }

    # 가짜 로그인 처리 (현재 인증된 사용자)
    def mock_get_current_user():
        return authenticated_user

    client.app.dependency_overrides[get_current_user] = mock_get_current_user

    # 게시글 생성 요청
    # when
    response = client.post("/posts/", json=post_data)

    # 응답 코드 확인
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"

    # DB 세션 명시적으로 커밋
    db_session.commit()

    # 게시글 생성 후 DB에서 조회
    created_post = (
        db_session.query(Post).filter(Post.title == post_data["title"]).first()
    )

    # 게시글이 생성되었는지 확인
    # then
    assert (
        created_post is not None
    ), "The post should exist in the database after creation."
    assert created_post.title == post_data["title"]
    assert created_post.content == post_data["content"]
    assert created_post.author_id == authenticated_user.userid  # 작성자가 올바른지 확인


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


def test_create_post_success(
    client: TestClient, db_session: Session, authenticated_user, set_mock_user
):
    # 게시글 데이터를 준비
    # given
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
    }

    # 게시글 생성 요청
    # when
    response = client.post("/posts/", json=post_data)

    # 응답 코드 확인
    # then
    assert response.status_code == 200

    # 게시글 생성 후 DB에서 조회
    created_post = (
        db_session.query(Post).filter(Post.title == post_data["title"]).first()
    )
    print(created_post)  # 디버그용으로 게시글 출력

    # 게시글이 생성되었는지 확인
    assert (
        created_post is not None
    ), "The post should exist in the database after creation."


def test_read_post_not_found(client):
    # 존재하지 않는 게시글 ID
    # given
    non_existing_post_id = 9999

    # 게시글 조회 API 호출
    # when
    response = client.get(f"/posts/{non_existing_post_id}")

    # 404 Not Found 상태 코드와 적절한 오류 메시지 확인
    # then
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "게시글이 없습니다."


def test_read_post_success(client: TestClient, db_session: Session, authenticated_user):
    # 게시글 데이터를 준비하고 Pydantic 모델 사용
    # given
    post_data = PostCreate(
        title="Test Post",
        content="This is a test post content.",
        author_id=authenticated_user.userid,
    )

    post_service = PostService(db_session)
    created_post = post_service.create(
        post_create=post_data, author_id=authenticated_user.userid
    )
    db_session.commit()

    # 게시글 조회 요청
    # when
    response = client.get(f"/posts/{created_post.id}")

    # 응답 상태 코드 및 내용 검증
    # then
    assert response.status_code == 200
    response_data = response.json()

    assert response_data["id"] == created_post.id
    assert response_data["title"] == created_post.title
    assert response_data["content"] == created_post.content
    assert response_data["author"]["userid"] == authenticated_user.userid


def test_read_post_not_found(client: TestClient):
    # 존재하지 않는 게시글 조회 시도
    # when
    response = client.get("/posts/99999")  # 없는 게시글 ID

    # 404 반환 확인
    # then
    assert response.status_code == 404
    assert response.json()["detail"] == "게시글이 없습니다."


def test_update_post_success(
    client: TestClient, db_session: Session, authenticated_user, set_mock_user
):
    # 게시글 생성
    # given
    post_data = {
        "title": "Old Title",
        "content": "Old content",
        "author_id": authenticated_user.userid,
    }
    post = Post(**post_data)
    db_session.add(post)
    db_session.commit()

    # 업데이트할 데이터 준비
    # when
    update_data = {
        "title": "New Title",
        "content": "New content",
    }
    post_update = PostUpdate(**update_data)

    # 게시글 업데이트 요청
    # then
    response = client.patch(f"/posts/{post.id}", json=update_data)

    # 응답 상태 코드 및 내용 확인
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["title"] == update_data["title"]
    assert response_data["content"] == update_data["content"]
    assert response_data["author"]["userid"] == authenticated_user.userid


def test_update_post_not_found(
    client: TestClient, db_session: Session, authenticated_user, set_mock_user
):
    # given
    update_data = {
        "title": "New Title",
        "content": "New content",
    }

    post_update = PostUpdate(**update_data)
    # 존재하지 않는 게시글 업데이트 시도
    # when
    response = client.patch("/posts/9999", json=update_data)  # 존재하지 않는 게시글 ID

    # 응답 상태 코드 확인 (404)
    # then
    assert response.status_code == 404
    assert response.json()["detail"] == "게시글이 없습니다."


# 게시글 삭제 성공 테스트
def test_delete_post_success(
    client: TestClient, db_session: Session, authenticated_user, set_mock_user
):
    # 게시글 생성
    # given
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
        "author_id": authenticated_user.userid,
    }
    post = Post(**post_data)
    db_session.add(post)
    db_session.commit()

    # 게시글 삭제 요청
    # when
    response = client.delete(f"/posts/{post.id}")

    # 응답 상태 코드 확인 (200 OK 기대)
    # then
    assert response.status_code == 200
    assert response.content == b""  # 응답 본문이 비어있는지 확인


def test_delete_post_not_found(
    client: TestClient, db_session: Session, authenticated_user, set_mock_user
):
    # 존재하지 않는 게시글 삭제 시도
    # when
    response = client.delete("/posts/9999")  # 존재하지 않는 게시글 ID

    # 응답 상태 코드 확인 (404)
    # then
    assert response.status_code == 404
    assert response.json()["detail"] == "게시글이 없습니다."


def test_read_posts_by_user_success(
    client: TestClient, db_session: Session, authenticated_user
):
    # 유저와 게시글 데이터를 미리 생성하여 DB에 저장
    # given
    post_data_1 = {
        "title": "First Test Post",
        "content": "This is the first test post content.",
        "author_id": authenticated_user.userid,  # 올바른 author_id 설정
    }
    post_1 = Post(**post_data_1)
    db_session.add(post_1)

    post_data_2 = {
        "title": "Second Test Post",
        "content": "This is the second test post content.",
        "author_id": authenticated_user.userid,  # 같은 유저가 작성한 두 번째 게시글
    }
    post_2 = Post(**post_data_2)
    db_session.add(post_2)

    db_session.commit()

    # 해당 유저가 작성한 게시글 목록을 요청
    # when
    response = client.get(f"/users/{authenticated_user.userid}/posts")

    # 응답 상태 코드 및 반환된 데이터 확인
    # then -
    assert response.status_code == 200
    response_data = response.json()

    assert len(response_data) == 2  # 작성된 게시글이 2개여야 함
    assert response_data[0]["title"] == post_data_1["title"]
    assert response_data[1]["title"] == post_data_2["title"]


def test_read_posts_by_user_pagination(
    client: TestClient, db_session: Session, authenticated_user
):
    # 15개의 게시글을 작성한 사용자 생성
    # given
    for i in range(15):
        post_data = {
            "title": f"Test Post {i + 1}",
            "content": f"This is test post content {i + 1}.",
            "author_id": authenticated_user.userid,
        }
        post = Post(**post_data)
        db_session.add(post)

    db_session.commit()

    # 첫 번째 페이지(10개)의 게시글 목록 요청
    # when
    response = client.get(f"/users/{authenticated_user.userid}/posts?skip=0&limit=10")
    assert response.status_code == 200
    response_data = response.json()

    # 10개의 게시글이 반환되었는지 확인
    # then
    assert len(response_data) == 10


def test_read_user_success(client: TestClient, db_session: Session):
    # 테스트용 사용자 데이터를 DB에 미리 저장
    # given
    user_data = {
        "userid": "testuser123",
        "hashed_password": get_password_hash("Testpassword1234"),  # 비밀번호 해시화
        "role": "MEMBER",
        "nickname": "tester",
    }
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    # 저장된 사용자의 userid로 GET 요청을 보냄
    # when
    response = client.get(f"/users/{user.userid}")  # 경로 변수로 userid 전달

    # 요청이 성공했는지 상태 코드 확인
    # then
    assert response.status_code == 200

    # 응답에서 반환된 데이터가 예상대로 UserRead 모델과 일치하는지 확인
    response_json = response.json()
    assert response_json["userid"] == user_data["userid"]
    assert response_json["nickname"] == user_data["nickname"]
    assert "created_at" in response_json  # 자동 생성된 필드가 있는지 확인


def test_read_user_not_found(client: TestClient):
    # 존재하지 않는 사용자 ID로 GET 요청을 보냄
    # when
    response = client.get(f"/users/fake")

    # 요청이 실패했는지 상태 코드 확인
    # Then
    assert response.status_code == 404
    response_json = response.json()
    assert response_json["detail"] == "유저가 없습니다."


def test_update_user_success(
    client: TestClient, db_session: Session, authenticated_user, set_mock_user
):
    # 기존 사용자 생성 (userid는 str 타입)
    # given
    user_data = {
        "userid": "testuser123",  # string 타입으로 설정
        "hashed_password": get_password_hash("OldPassword1234"),
        "role": "MEMBER",
        "nickname": "testuser",
    }
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    # 수정할 데이터 준비 (Pydantic 스키마에 맞게 구성)
    # when
    update_data = {"password": "NewPassword1234", "nickname": "tester_updated"}

    # 테스트용으로 authenticated_user의 userid를 생성한 user의 userid로 설정
    authenticated_user.userid = user_data["userid"]
    # 사용자 업데이트 요청
    response = client.patch(f"/users/{user.userid}", json=update_data)

    # 응답 코드 확인
    # then
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"


def test_update_user_unauthorized(
    client: TestClient, db_session: Session, unauthorized_user, set_mock_user
):
    # 기존 사용자 생성
    # given
    user_data = {
        "userid": "testuser123",
        "hashed_password": "fakehashedpassword",
        "role": "MEMBER",
        "nickname": "testuser",
    }
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    update_data = {"password": "NewPassword1234", "nickname": "tester_updated"}

    # 사용자를 업데이트하려고 시도
    # when
    response = client.patch(f"/users/{user.userid}", json=update_data)

    # 응답 코드가 403 Forbidden이어야 함
    # then
    assert response.status_code == 403, f"Expected 403 but got {response.status_code}"


def test_delete_user_success(db_session: Session):
    # 테스트용 유저 생성
    # given
    user_data = {
        "userid": "testuser123",
        "hashed_password": "hashedpassword123",
        "role": "MEMBER",
        "nickname": "testnickname",
    }
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()

    # delete_user 메서드 호출
    # when
    user_service = UserService(db_session)
    user_service.delete(userid="testuser123")

    # DB에서 해당 유저가 삭제되었는지 확인
    deleted_user = db_session.query(User).filter(User.userid == "testuser123").first()

    # then
    assert deleted_user is None, "User should be deleted from the database."


def test_delete_user_not_found(db_session: Session):
    # 존재하지 않는 사용자 ID를 삭제하려고 시도
    # given
    user_service = UserService(db_session)

    # when
    with pytest.raises(ValueError) as exc_info:
        user_service.delete(userid="nonexistent_user")

    # then
    assert str(exc_info.value) == "유저가 없습니다."


def test_create_comment_success(
    client: TestClient, db_session: Session, authenticated_user, set_mock_user
):
    # 게시글 생성
    # given
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
        "author_id": authenticated_user.userid,  # author_id를 올바르게 설정
    }
    post = Post(**post_data)
    db_session.add(post)
    db_session.commit()

    # 댓글 데이터 생성
    # when
    comment_data = {
        "content": "This is a test comment.",
        "post_id": post.id,
        "author_id": authenticated_user.userid,  # author_id를 올바르게 설정
    }

    # 댓글 생성 요청
    # then
    response = client.post("/comments/", json=comment_data)

    # 응답 상태 코드 및 생성된 댓글 확인
    assert response.status_code == 200
    response_data = response.json()

    # 댓글 내용 및 작성자 확인
    assert response_data["content"] == comment_data["content"]
    assert response_data["author_id"] == authenticated_user.userid
    assert response_data["post_id"] == post.id


def test_read_comment_success(
    client: TestClient, db_session: Session, authenticated_user
):
    # 게시글과 댓글 데이터를 미리 생성하여 DB에 저장
    # given
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
        "author_id": authenticated_user.userid,
    }
    post = Post(**post_data)
    db_session.add(post)
    db_session.commit()

    comment_data = {
        "content": "This is a test comment.",
        "post_id": post.id,
        "author_id": authenticated_user.userid,
    }
    comment = Comment(**comment_data)
    db_session.add(comment)
    db_session.commit()

    # 생성된 댓글을 읽는 요청
    # when
    response = client.get(f"/comments/{comment.id}")

    # 응답 상태 코드 및 내용 검증
    # then
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["content"] == comment_data["content"]
    assert response_data["post_id"] == comment_data["post_id"]
    assert response_data["author_id"] == comment_data["author_id"]


def test_read_comment_not_found(client: TestClient):
    # 존재하지 않는 댓글 ID로 요청
    # given
    non_existent_comment_id = 999

    # 존재하지 않는 댓글을 읽는 요청
    # when
    response = client.get(f"/comments/{non_existent_comment_id}")

    # 404 응답이 반환되어야 함
    # then
    assert response.status_code == 404
    assert response.json()["detail"] == "댓글이 없습니다."


def test_update_comment_success(
    client: TestClient, db_session: Session, authenticated_user, set_mock_user
):
    # 게시글과 댓글 데이터를 미리 생성하여 DB에 저장
    # given
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
        "author_id": authenticated_user.userid,
    }
    post = Post(**post_data)
    db_session.add(post)
    db_session.commit()

    comment_data = {
        "content": "This is a test comment.",
        "post_id": post.id,
        "author_id": authenticated_user.userid,
    }
    comment = Comment(**comment_data)
    db_session.add(comment)
    db_session.commit()

    # 수정할 댓글 데이터 준비
    update_data = {"content": "Updated comment content."}

    # 댓글 수정 요청
    # when
    response = client.patch(f"/comments/{comment.id}", json=update_data)

    # 응답 상태 코드 및 내용 검증
    # then
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["content"] == update_data["content"]


def test_update_comment_not_found(client: TestClient, authenticated_user):
    # 가짜 로그인 처리 (현재 인증된 사용자)
    def mock_get_current_user():
        return authenticated_user

    client.app.dependency_overrides[get_current_user] = mock_get_current_user
    # 존재하지 않는 댓글 ID로 수정 요청
    # when
    update_data = {"content": "Updated comment content."}
    non_existent_comment_id = 999
    response = client.patch(f"/comments/{non_existent_comment_id}", json=update_data)

    # 404 응답이 반환되어야 함
    # then
    assert response.status_code == 404
    assert response.json()["detail"] == "댓글이 없습니다."


def test_delete_comment_success(
    client: TestClient, db_session: Session, authenticated_user, set_mock_user
):
    # 게시글과 댓글 데이터를 미리 생성하여 DB에 저장
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
        "author_id": authenticated_user.userid,
    }
    post = Post(**post_data)
    db_session.add(post)
    db_session.commit()

    comment_data = {
        "content": "This is a test comment.",
        "post_id": post.id,
        "author_id": authenticated_user.userid,
    }
    comment = Comment(**comment_data)
    db_session.add(comment)
    db_session.commit()

    response = client.delete(f"/comments/{comment.id}")

    # 응답 상태 코드 확인 (200 OK)
    assert response.status_code == 200

    # 세션 커밋 후 삭제 상태 확인
    db_session.commit()  # 명시적으로 커밋 호출

    # DB에서 댓글이 삭제되었는지 확인
    deleted_comment = db_session.query(Comment).filter(Comment.id == comment.id).first()

    # 댓글이 삭제되었는지 확인 (None이어야 함)
    assert deleted_comment is None, "The comment should be deleted from the database."


def test_delete_comment_forbidden(
    client: TestClient,
    db_session: Session,
    authenticated_user,
    other_user,
    set_mock_user,
):
    # 게시글과 다른 사용자가 작성한 댓글 데이터를 미리 생성하여 DB에 저장
    # given
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
        "author_id": authenticated_user.userid,
    }
    post = Post(**post_data)
    db_session.add(post)
    db_session.commit()

    comment_data = {
        "content": "This is a test comment.",
        "post_id": post.id,
        "author_id": other_user.userid,  # 다른 사용자가 작성한 댓글
    }
    comment = Comment(**comment_data)
    db_session.add(comment)
    db_session.commit()

    # 댓글 삭제 요청 (권한 없음)
    # when
    response = client.delete(f"/comments/{comment.id}")

    # 403 Forbidden 응답 확인
    # then
    assert response.status_code == 403
    assert response.json()["detail"] == "댓글 삭제 권한이 없습니다."


def test_read_comments_by_post_success(
    client: TestClient, db_session: Session, authenticated_user
):
    # 게시글과 댓글 데이터를 미리 생성하여 DB에 저장
    # given
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
        "author_id": authenticated_user.userid,
    }
    post = Post(**post_data)
    db_session.add(post)
    db_session.commit()

    comment_data_1 = {
        "content": "This is the first test comment.",
        "post_id": post.id,
        "author_id": authenticated_user.userid,
    }
    comment_1 = Comment(**comment_data_1)
    db_session.add(comment_1)

    comment_data_2 = {
        "content": "This is the second test comment.",
        "post_id": post.id,
        "author_id": authenticated_user.userid,
    }
    comment_2 = Comment(**comment_data_2)
    db_session.add(comment_2)

    db_session.commit()

    # 게시글에 달린 댓글 목록 요청
    # when
    response = client.get(f"/posts/{post.id}/comments")

    # 응답 상태 코드 및 반환된 데이터 검증
    # then
    assert response.status_code == 200
    response_data = response.json()

    assert len(response_data) == 2
    assert response_data[0]["content"] == comment_data_1["content"]
    assert response_data[1]["content"] == comment_data_2["content"]
    assert response_data[0]["author_id"] == authenticated_user.userid
    assert response_data[1]["author_id"] == authenticated_user.userid


def test_read_comments_by_post_pagination(
    client: TestClient, db_session: Session, authenticated_user
):
    # 여러 개의 댓글이 달린 게시글 생성
    # given
    post_data = {
        "title": "Test Post with Multiple Comments",
        "content": "This is a test post with multiple comments.",
        "author_id": authenticated_user.userid,
    }
    post = Post(**post_data)
    db_session.add(post)
    db_session.commit()

    # 15개의 댓글 생성
    for i in range(15):
        comment_data = {
            "content": f"Test comment {i + 1}",
            "post_id": post.id,
            "author_id": authenticated_user.userid,
        }
        comment = Comment(**comment_data)
        db_session.add(comment)

    db_session.commit()

    # 페이지네이션을 적용하여 첫 번째 페이지의 댓글(10개) 요청
    # when
    response = client.get(f"/posts/{post.id}/comments?skip=0&limit=10")
    assert response.status_code == 200
    response_data = response.json()

    # 댓글 10개가 반환되었는지 확인
    # then
    assert len(response_data) == 10
