from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.domain.models.post import Post
from app.domain.schemas.post import PostCreate, PostRead, PostUpdate


class PostService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, post_create: PostCreate, author_id: int) -> Post:
        post = Post(
            author_id=author_id,
            title=post_create.title,
            content=post_create.content,
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_multi(self, skip: int = 0, limit: int = 10) -> List[Post]:
        return self.db.query(Post).offset(skip).limit(limit).all()

    def get(self, post_id: int) -> Optional[Post]:
        return (
            self.db.query(Post)
            .options(joinedload(Post.author))
            .filter(Post.id == post_id)
            .first()
        )

    def update(self, post_id: int, post_update: PostCreate) -> Post:
        post = self.db.query(Post).filter(Post.id == post_id).first()
        for key, value in post_update.dict(exclude_unset=True).items():
            setattr(post, key, value)
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post_id: int):
        post = self.db.query(Post).filter(Post.id == post_id).first()
        self.db.delete(post)
        self.db.commit()

    def _get_post_by_id(self, post_id: int) -> Post:
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="게시글이 없습니다."
            )
        return post
