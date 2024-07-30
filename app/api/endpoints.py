from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.domain.schemas.schemas import PostCreate, PostRead, PostUpdate
from app.service.user_service import PostService

router = APIRouter()


@router.post("/posts/", response_model=PostRead)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    return PostService(db).create_post(post)


@router.get("/posts/{post_id}", response_model=PostRead)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = PostService(db).get_post(post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 없습니다."
        )
    return post


@router.get("/posts/", response_model=List[PostRead])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return PostService(db).get_posts(skip=skip, limit=limit)


@router.patch("/posts/{post_id}", response_model=PostRead)
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db)):
    service = PostService(db)
    db_post = service.get_post(post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 없습니다."
        )
    try:
        return service.update_post(post_id, post)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete("/posts/{post_id}", response_model=PostRead)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    service = PostService(db)
    db_post = service.get_post(post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 없습니다."
        )
    service.delete_post(post_id)
    return Response(status_code=status.HTTP_200_OK)
