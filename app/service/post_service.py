from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from app.domain.models.post import Post
from app.domain.schemas.post import PostCreate, PostRead, PostUpdate


class PostService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, post_create: PostCreate, author_id: int) -> PostRead:
        post = Post(
            author_id=author_id,
            title=post_create.title,
            content=post_create.content,
            created_at=datetime.utcnow(),
        )
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return PostRead.from_orm(post)

    def get(self, post_id: int) -> PostRead:
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if post:
            return PostRead.from_orm(post)
        return None

    def get_multi(self, skip: int = 0, limit: int = 10) -> List[PostRead]:
        posts = self.db.query(Post).offset(skip).limit(limit).all()
        return [PostRead.from_orm(post) for post in posts]

    def get_by_author(
        self, author_id: int, skip: int = 0, limit: int = 10
    ) -> List[PostRead]:
        posts = (
            self.db.query(Post)
            .filter(Post.author_id == author_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [PostRead.from_orm(post) for post in posts]

    def update(self, post_id: int, post_update: PostUpdate) -> PostRead:
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise ValueError("게시글이 없습니다.")
        for key, value in post_update.dict(exclude_unset=True).items():
            setattr(post, key, value)
        self.db.commit()
        self.db.refresh(post)
        return PostRead.from_orm(post)

    def delete(self, post_id: int):
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if post:
            self.db.delete(post)
            self.db.commit()
