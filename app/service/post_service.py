from typing import List

from sqlalchemy.orm import Session

from app.domain.models.post import Post
from app.domain.schemas.post import PostCreate, PostRead, PostUpdate
from app.service.base_service import BaseService


class PostService(BaseService[Post, PostCreate, PostUpdate]):
    def __init__(self, db: Session):
        super().__init__(Post, db)

    def get_by_author(
        self, author_id: int, skip: int = 0, limit: int = 10
    ) -> List[Post]:
        return (
            self.db.query(Post)
            .filter(Post.author == author_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
