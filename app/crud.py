from datetime import datetime

from sqlalchemy.orm import Session

from .models import Post
from .schemas import PostCreate, PostUpdate


def create_post(db: Session, post_create: PostCreate) -> Post:
    db_post = Post(**post_create.dict(), created_at=datetime.utcnow())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post(db: Session, post_id: int) -> Post:
    return db.query(Post).filter(Post.id == post_id).first()


def get_posts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Post).offset(skip).limit(limit).all()


def update_post(db: Session, post_id: int, post_update: PostUpdate) -> Post:
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post:
        if post_update.author and db_post.author != post_update.author:
            raise ValueError("사용자가 다릅니다..")
        update_data = post_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_post, key, value)
        db_post.created_at = datetime.utcnow()
        db.commit()
        db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int) -> Post:
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
