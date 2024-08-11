from typing import List

from sqlalchemy.orm import Session

from app.domain.models.models import Post
from app.domain.schemas.schemas import PostCreate, PostRead, PostUpdate


class PostService:
    def __init__(self, db: Session):
        self.db = db

    def create_post(self, post_create: PostCreate) -> PostRead:
        post = Post(**post_create.dict())
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return PostRead.from_orm(post)

    def get_post(self, post_id: int) -> PostRead:
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if post:
            return PostRead.from_orm(post)
        return None

    def get_posts(self, skip: int = 0, limit: int = 10) -> List[PostRead]:
        posts = self.db.query(Post).offset(skip).limit(limit).all()
        return [PostRead.from_orm(post) for post in posts]

    def update_post(self, post_id: int, post_update: PostUpdate) -> PostRead:
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise ValueError("게시글이 없습니다.")
        for key, value in post_update.dict(exclude_unset=True).items():
            setattr(post, key, value)
        self.db.commit()
        self.db.refresh(post)
        return PostRead.from_orm(post)

    def delete_post(self, post_id: int):
        post = self.db.query(Post).filter(Post.id == post_id).first()
        if post:
            self.db.delete(post)
            self.db.commit()
