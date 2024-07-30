from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.domain.schemas.post import PostCreate, PostRead, PostUpdate
from app.domain.schemas.user import UserCreate, UserRead, UserUpdate
from app.service.comment_service import CommentService
from app.service.post_service import PostService
from app.service.user_service import UserService

router = APIRouter()


# Post Endpoints
@router.post("/posts/", response_model=PostRead)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    return PostService(db).create(post)


@router.get("/posts/{post_id}", response_model=PostRead)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = PostService(db).get(post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 없습니다."
        )
    return post


@router.get("/posts/", response_model=List[PostRead])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return PostService(db).get_multi(skip=skip, limit=limit)


@router.patch("/posts/{post_id}", response_model=PostRead)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    try:
        return PostService(db).update(post_id, post)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/posts/{post_id}", response_model=PostRead)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    try:
        PostService(db).delete(post_id)
        return Response(status_code=status.HTTP_200_OK)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/users/{user_id}/posts", response_model=List[PostRead])
def read_posts_by_user(
    user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    return PostService(db).get_by_author(user_id, skip=skip, limit=limit)


# User Endpoints
@router.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).create(user)


@router.get("/users/{user_id}", response_model=UserRead)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = UserService(db).get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="유저가 없습니다."
        )
    return user


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    try:
        return UserService(db).update(user_id, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/users/{user_id}", response_model=UserRead)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    try:
        UserService(db).delete(user_id)
        return Response(status_code=status.HTTP_200_OK)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/users/{user_id}/comments", response_model=List[CommentRead])
def read_comments_by_user(
    user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    return UserService(db).get_comments_by_user(user_id, skip=skip, limit=limit)


# Comment Endpoints
@router.post("/comments/", response_model=CommentRead)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    return CommentService(db).create(comment)


@router.get("/comments/{comment_id}", response_model=CommentRead)
def read_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = CommentService(db).get(comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="댓글이 없습니다."
        )
    return comment


@router.patch("/comments/{comment_id}", response_model=CommentRead)
def update_comment(
    comment_id: int, comment: CommentUpdate, db: Session = Depends(get_db)
):
    try:
        return CommentService(db).update(comment_id, comment)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/comments/{comment_id}", response_model=CommentRead)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    try:
        CommentService(db).delete(comment_id)
        return Response(status_code=status.HTTP_200_OK)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/posts/{post_id}/comments", response_model=List[CommentRead])
def read_comments_by_post(
    post_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    return CommentService(db).get_by_post(post_id, skip=skip, limit=limit)
