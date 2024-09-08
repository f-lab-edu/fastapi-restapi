# test_endpoints.py

import pytest
from fastapi import status

from app.domain.schemas.comment import CommentCreate, CommentUpdate
from app.domain.schemas.post import PostCreate, PostUpdate


# User 엔드포인트 테스트
def test_create_user_success(client, db_session):
    # TODO: 아래 given when then으로 모두 표현하기 (검색해보기)
    # TODO: 테스트 코드에도 타입 힌팅 추가
    # given
    user_data = {
        "role": "MEMBER",
        "userid": "testuser2",
        "nickname": "tester2",
        "password": "testpassword2",
    }

    # when
    response = client.post("/users/", json=user_data)

    # then
    # TODO: assert로 누락된 검증할 부분 추가하기 (API 리스폰스 바디, DB에 생성된 엔티티 확인)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == "MEMBER"
    assert response.json()["userid"] == "testuser2"
    assert response.json()["nickname"] == "testuser2"
    assert "id" in response.json()
    assert "created_at" in response.json()


def test_create_user_failure(client):
    # given
    user_data = {"username": "testuser"}  # password 미포함

    # when
    response = client.post("/users/", json=user_data)

    # then
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    #       "msg": "Value error, 비밀번호는 8자 이상이어야 합니다.",이것도 나와야함


def test_read_user_success(client, auth_headers):
    # when
    response = client.get("/users/1", headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["role"] == "MEMBER"
    assert response.json()["userid"] == "testuser2"
    assert response.json()["nickname"] == "testuser2"
    assert "id" in response.json()
    assert "created_at" in response.json()


def test_read_user_failure(client, auth_headers):
    # when
    response = client.get("/users/999", headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Post 엔드포인트 테스트
def test_create_post_success(client, auth_headers):
    # given
    post_data = {
        "title": "Test Post",
        "content": "This is a test post.",
    }

    # when
    response = client.post("/posts/", json=post_data, headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()
    assert response.json()["title"] == "Test Post"
    assert "author" in response.json()
    assert "created_at" in response.json()


def test_create_post_failure(client, auth_headers):
    # given
    post_data = {"title": "Test Post"}  # content 누락

    # when
    response = client.post("/posts/", json=post_data, headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_read_post_success(client, auth_headers):
    # 이전 테스트에서 생성된 Post의 ID 사용
    # when
    response = client.get("/posts/1", headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()
    assert response.json()["title"] == "Test Post"
    assert response.json()["content"] == "This is a test post."


def test_read_post_failure(client):
    # when
    response = client.get("/posts/999")

    # then
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_post_success(client, auth_headers):
    # given
    post_update_data = {"title": "Updated Test Post", "content": "Updated content"}

    # when
    response = client.patch("/posts/1", json=post_update_data, headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()
    assert response.json()["title"] == "Updated Test Post"
    assert response.json()["content"] == "Updated content"
    assert "author" in response.json()


def test_update_post_failure(client, auth_headers):
    # given
    post_update_data = {"title": "Fail Update"}  # content 누락

    # when
    response = client.patch("/posts/1", json=post_update_data, headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_post_success(client, auth_headers):
    # when
    response = client.delete("/posts/1", headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_200_OK


def test_delete_post_failure(client, auth_headers):
    # when
    response = client.delete("/posts/999", headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Comment 엔드포인트 테스트
def test_create_comment_success(client, auth_headers):
    # Post 작성 후 해당 ID로 Comment 생성
    # givne
    post_data = {"title": "Another Test Post", "content": "This is another test post."}

    # when
    post_response = client.post("/posts/", json=post_data, headers=auth_headers)
    post_id = post_response.json()["id"]
    comment_data = {"content": "This is a comment", "post_id": post_id}
    response = client.post("/comments/", json=comment_data, headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()
    assert "author_id" in response.json()
    assert "post_id" in response.json()
    assert response.json()["content"] == "This is a comment"
    assert "created_at" in response.json()


def test_create_comment_failure(client, auth_headers):
    # 잘못된 Post ID로 댓글 생성 시도
    # given
    comment_data = {"content": "This is a comment", "post_id": 9999}

    # when
    response = client.post("/comments/", json=comment_data, headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_comment_success(client, auth_headers):
    # when
    response = client.get("/comments/1", headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_200_OK
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()
    assert "author_id" in response.json()
    assert "post_id" in response.json()
    assert response.json()["content"] == "This is a comment"
    assert "created_at" in response.json()


def test_read_comment_failure(client):
    # when
    response = client.get("/comments/999")

    # then
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_comment_success(client, auth_headers):
    # given
    comment_update_data = {"content": "Updated Comment"}

    # when
    response = client.patch(
        "/comments/1", json=comment_update_data, headers=auth_headers
    )

    # then
    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()
    assert "author_id" in response.json()
    assert "post_id" in response.json()
    assert response.json()["content"] == "Updated Comment"
    assert "created_at" in response.json()


def test_update_comment_failure(client, auth_headers):
    # given
    comment_update_data = {"content": ""}  # 빈 내용

    # when
    response = client.patch(
        "/comments/1", json=comment_update_data, headers=auth_headers
    )

    # then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_comment_success(client, auth_headers):
    # when
    response = client.delete("/comments/1", headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_200_OK


def test_delete_comment_failure(client, auth_headers):
    # when
    response = client.delete("/comments/999", headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_404_NOT_FOUND


# 기타 엔드포인트에 대한 테스트 (예: 로그인/로그아웃)
def test_login_success(client):
    # given
    response = client.post(
        "/login", data={"username": "testuser", "password": "testpassword"}
    )

    # then
    assert response.status_code == status.HTTP_200_OK
    assert "session_id" in response.json()


def test_login_failure(client):
    # given
    response = client.post(
        "/login", data={"username": "wronguser", "password": "wrongpassword"}
    )

    # then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_success(client, auth_headers):
    # when
    response = client.post("/logout", headers=auth_headers)

    # then
    assert response.status_code == status.HTTP_200_OK


def test_logout_failure(client):
    # when
    response = client.post("/logout")  # 비인증 사용자

    # then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
