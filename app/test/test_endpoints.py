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
        "username": "testuser2",
        "password": "testpassword2",
        "nickname": "tester2",
    }

    # when
    response = client.post("/users/", json=user_data)

    # then
    # TODO: assert로 누락된 검증할 부분 추가하기 (API 리스폰스 바디, DB에 생성된 엔티티 확인)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser2"


def test_create_user_failure(client):
    user_data = {"username": "testuser"}  # password 미포함
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_read_user_success(client, auth_headers):
    response = client.get("/users/1", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"


def test_read_user_failure(client, auth_headers):
    response = client.get("/users/999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Post 엔드포인트 테스트
def test_create_post_success(client, auth_headers):
    post_data = {"title": "Test Post", "content": "This is a test post."}
    response = client.post("/posts/", json=post_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Test Post"


def test_create_post_failure(client, auth_headers):
    post_data = {"title": "Test Post"}  # content 누락
    response = client.post("/posts/", json=post_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_read_post_success(client, auth_headers):
    # 이전 테스트에서 생성된 Post의 ID 사용
    response = client.get("/posts/1", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Test Post"


def test_read_post_failure(client):
    response = client.get("/posts/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_post_success(client, auth_headers):
    post_update_data = {"title": "Updated Test Post", "content": "Updated content"}
    response = client.patch("/posts/1", json=post_update_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Test Post"


def test_update_post_failure(client, auth_headers):
    post_update_data = {"title": "Fail Update"}  # content 누락
    response = client.patch("/posts/1", json=post_update_data, headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_post_success(client, auth_headers):
    response = client.delete("/posts/1", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK


def test_delete_post_failure(client, auth_headers):
    response = client.delete("/posts/999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


# Comment 엔드포인트 테스트
def test_create_comment_success(client, auth_headers):
    # Post 작성 후 해당 ID로 Comment 생성
    post_data = {"title": "Another Test Post", "content": "This is another test post."}
    post_response = client.post("/posts/", json=post_data, headers=auth_headers)
    post_id = post_response.json()["id"]

    comment_data = {"content": "This is a comment", "post_id": post_id}
    response = client.post("/comments/", json=comment_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content"] == "This is a comment"


def test_create_comment_failure(client, auth_headers):
    # 잘못된 Post ID로 댓글 생성 시도
    comment_data = {"content": "This is a comment", "post_id": 9999}
    response = client.post("/comments/", json=comment_data, headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_comment_success(client, auth_headers):
    response = client.get("/comments/1", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content"] == "This is a comment"


def test_read_comment_failure(client):
    response = client.get("/comments/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_comment_success(client, auth_headers):
    comment_update_data = {"content": "Updated Comment"}
    response = client.patch(
        "/comments/1", json=comment_update_data, headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content"] == "Updated Comment"


def test_update_comment_failure(client, auth_headers):
    comment_update_data = {"content": ""}  # 빈 내용
    response = client.patch(
        "/comments/1", json=comment_update_data, headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_comment_success(client, auth_headers):
    response = client.delete("/comments/1", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK


def test_delete_comment_failure(client, auth_headers):
    response = client.delete("/comments/999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


# 기타 엔드포인트에 대한 테스트 (예: 로그인/로그아웃)
def test_login_success(client):
    response = client.post(
        "/login", data={"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "session_id" in response.json()


def test_login_failure(client):
    response = client.post(
        "/login", data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_logout_success(client, auth_headers):
    response = client.post("/logout", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK


def test_logout_failure(client):
    response = client.post("/logout")  # 비인증 사용자
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
