from datetime import timedelta
from typing import List

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.utils import get_password_hash, verify_password
from app.database import get_db
from app.domain.models.post import Post
from app.domain.models.user import Role
from app.domain.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.domain.schemas.post import PostCreate, PostRead, PostUpdate
from app.domain.schemas.user import UserCreate, UserInDB, UserRead, UserUpdate
from app.service.comment_service import CommentService
from app.service.post_service import PostService
from app.service.user_service import UserService
from app.session_store import session_store

router = APIRouter()


# 권한 체크 함수: 요청자가 본인인지 또는 관리자 권한을 가지고 있는지 확인
def is_owner_or_admin(current_user: UserInDB, owner_id: int) -> bool:
    return current_user.userid == owner_id or current_user.role == Role.ADMIN


@router.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # 비밀번호를 해시화하지 않고 그대로 전달
        print(f"입력된 비밀번호: {user.password}")

        user_service = UserService(db)
        new_user = user_service.create_user(user)

        # 데이터베이스 커밋 후 로그 출력
        print("데이터베이스 커밋 성공")
        db.commit()

        return new_user
    except Exception as e:
        print(f"회원가입 중 에러 발생: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/posts/", response_model=PostRead)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    try:
        post_service = PostService(db)
        new_post = post_service.create(post_create=post, author_id=current_user.userid)
        db.commit()
        return new_post
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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


def get_multi(self, skip: int = 0, limit: int = 10) -> List[Post]:
    return self.db.query(Post).offset(skip).limit(limit).all()


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
    print(
        f"current_user.id: {current_user.userid}, post_in_db.author_id: {post_in_db.author_id}"
    )

    if not is_owner_or_admin(current_user, post_in_db.author_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시글 수정 권한이 없습니다.",
        )

    try:
        updated_post = post_service.update(post_id, post)
        db.commit()
        return updated_post
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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

    try:
        post_service.delete(post_id)
        db.commit()
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users/{user_id}/posts", response_model=List[PostRead])
def read_posts_by_user(
    user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    return PostService(db).get_by_author(user_id, skip=skip, limit=limit)


# User Endpoints
@router.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        user.password = get_password_hash(user.password)
        new_user = UserService(db).create(user)
        db.commit()
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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

    try:
        updated_user = UserService(db).update(user_id, user)
        db.commit()
        return updated_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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

    try:
        UserService(db).delete(user_id)
        db.commit()
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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
    try:
        comment_service = CommentService(db)
        # current_user의 id를 author_id로 사용
        new_comment = comment_service.create(comment, author_id=current_user.userid)
        db.commit()
        return new_comment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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

    try:
        updated_comment = comment_service.update(comment_id, comment)
        db.commit()
        return updated_comment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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

    try:
        comment_service.delete(comment_id)
        db.commit()
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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


@router.post("/login")
def login_for_session(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = Response(),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)

    # 사용자 이름으로 사용자 정보 조회
    user = user_service.get_by_userid(form_data.username)

    # 사용자 이름 및 비밀번호 확인
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # 세션 생성 시 모든 유저 정보를 포함시킴
    session_data = {
        "userid": user.userid,
        "nickname": user.nickname,
        "hashed_password": user.hashed_password,
        "role": user.role,
        "id": user.id,
        "created_at": str(user.created_at),
    }

    # 세션 생성 (1일 만료)
    session_id = session_store.create_session(
        session_data, expires_in=timedelta(days=1)
    )

    # 세션 ID 쿠키로 설정
    response.set_cookie(key="session_id", value=session_id, httponly=True)

    # 세션 ID를 응답으로 반환
    return {"message": "Login successful", "session_id": session_id}


@router.post("/logout")
def logout(response: Response, session_id: str = Cookie(None)):
    session_store.delete_session(session_id)  # 세션 삭제
    response.delete_cookie("session_id")  # 쿠키에서 세션 ID 제거
    return {"message": "Logout successful"}
