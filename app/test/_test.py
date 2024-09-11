import pytest
from fastapi import status
from fastapi.testclient import TestClient


def test_create_user(client: TestClient):
    response = client.post(
        "/api/users/",
        json={
            "userid": "testuser",
            "nickname": "TestUser",
            "password": "TestPass1!",
            "role": "MEMBER",
        },
    )
    response.status_code == status.HTTP_200_OK
    assert response.json()["userid"] == "testuser"


def test_get_user(client: TestClient):
    response = client.get("/api/users/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1


def test_update_user(client: TestClient):
    response = client.patch("/api/users/1", json={"nickname": "UpdatedUser"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nickname"] == "UpdatedUser"


def test_delete_user(client: TestClient):
    response = client.delete("/api/users/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "User deleted successfully."}


# Tests for Post Endpoints
def test_create_post(client: TestClient):
    # User Creation and Login (replace with actual login flow if required)
    client.post(
        "/api/users/",
        json={
            "userid": "postuser",
            "nickname": "PostUser",
            "password": "PostPass1!",
            "role": "MEMBER",
        },
    )
    login_response = client.post(
        "/api/login", data={"username": "postuser", "password": "PostPass1!"}
    )
    token = login_response.cookies.get("session_id")

    response = client.post(
        "/api/posts/",
        json={"title": "Test Title", "content": "Test Content"},
        cookies={"session_id": token},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Test Title"


def test_get_post(client: TestClient):
    response = client.get("/api/posts/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1


def test_update_post(client: TestClient):
    response = client.patch(
        "/api/posts/1", json={"title": "Updated Title", "content": "Updated Content"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Updated Title"


def test_delete_post(client: TestClient):
    response = client.delete("/api/posts/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "Post deleted successfully."}


# Tests for Comment Endpoints
def test_create_comment(client: TestClient):
    # User and Post Creation (replace with actual login flow if required)
    client.post(
        "/api/users/",
        json={
            "userid": "commentuser",
            "nickname": "CommentUser",
            "password": "CommentPass1!",
            "role": "MEMBER",
        },
    )
    login_response = client.post(
        "/api/login", data={"username": "commentuser", "password": "CommentPass1!"}
    )
    token = login_response.cookies.get("session_id")

    # Create a post to comment on
    client.post(
        "/api/posts/",
        json={"title": "Post for Comment", "content": "Content of the post"},
        cookies={"session_id": token},
    )

    response = client.post(
        "/api/comments/",
        json={"post_id": 1, "content": "Test Comment"},
        cookies={"session_id": token},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content"] == "Test Comment"


def test_get_comment(client: TestClient):
    response = client.get("/api/comments/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 1


def test_update_comment(client: TestClient):
    response = client.patch("/api/comments/1", json={"content": "Updated Comment"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content"] == "Updated Comment"


def test_delete_comment(client: TestClient):
    response = client.delete("/api/comments/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"msg": "Comment deleted successfully."}
