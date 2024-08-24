from typing import List

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.utils import get_password_hash
from app.database import get_db
from app.domain.models.user import Role
from app.domain.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.domain.schemas.post import PostCreate, PostRead, PostUpdate
from app.domain.schemas.user import UserCreate, UserInDB, UserRead, UserUpdate
from app.service.comment_service import CommentService
from app.service.post_service import PostService
from app.service.user_service import UserService
from app.session import session_store

router = APIRouter()


# 권한 체크 함수: 요청자가 본인인지 또는 관리자 권한을 가지고 있는지 확인
def is_owner_or_admin(current_user: UserInDB, owner_id: int) -> bool:
    return current_user.id == owner_id or current_user.role == Role.ADMIN


# Post Endpoints
@router.post("/posts/", response_model=PostRead)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    post_service = PostService(db)
    return post_service.create(post, author_id=current_user.id)


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
def update_post(
    post_id: int,
    post: PostUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    post_service = PostService(db)
    post_in_db = post_service.get(post_id)
    if post_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 없습니다."
        )

    if not is_owner_or_admin(current_user, post_in_db.author_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시글 수정 권한이 없습니다.",
        )

    return post_service.update(post_id, post)


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    post_service = PostService(db)
    post_in_db = post_service.get(post_id)
    if post_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 없습니다."
        )

    if not is_owner_or_admin(current_user, post_in_db.author_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시글 삭제 권한이 없습니다.",
        )

    post_service.delete(post_id)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/users/{user_id}/posts", response_model=List[PostRead])
def read_posts_by_user(
    user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    return PostService(db).get_by_author(user_id, skip=skip, limit=limit)


# User Endpoints
@router.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user.password = get_password_hash(user.password)
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
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    if user.password:
        user.password = get_password_hash(user.password)

    if not is_owner_or_admin(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="유저 정보를 수정할 권한이 없습니다.",
        )

    return UserService(db).update(user_id, user)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    if not is_owner_or_admin(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="유저를 삭제할 권한이 없습니다.",
        )

    UserService(db).delete(user_id)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/users/{user_id}/comments", response_model=List[CommentRead])
def read_comments_by_user(
    user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    return UserService(db).get_comments_by_user(user_id, skip=skip, limit=limit)


# Comment Endpoints
@router.post("/comments/", response_model=CommentRead)
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    comment_service = CommentService(db)
    return comment_service.create(comment)


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
    comment_id: int,
    comment: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    comment_service = CommentService(db)
    comment_in_db = comment_service.get(comment_id)
    if comment_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="댓글이 없습니다."
        )

    if not is_owner_or_admin(current_user, comment_in_db.author_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="댓글 수정 권한이 없습니다.",
        )

    return comment_service.update(comment_id, comment)


@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    comment_service = CommentService(db)
    comment_in_db = comment_service.get(comment_id)
    if comment_in_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="댓글이 없습니다."
        )

    if not is_owner_or_admin(current_user, comment_in_db.author_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="댓글 삭제 권한이 없습니다.",
        )

    comment_service.delete(comment_id)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/posts/{post_id}/comments", response_model=List[CommentRead])
def read_comments_by_post(
    post_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    return CommentService(db).get_by_post(post_id, skip=skip, limit=limit)


# 세션 기반 프로필 정보 확인
@router.get("/profile")
def get_user_profile(session_id: str = Cookie(None)):
    session_data = session_store.get_session(session_id)

    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="세션을 찾을 수 없거나 만료되었습니다.",
        )

    return {"user": session_data["username"]}
