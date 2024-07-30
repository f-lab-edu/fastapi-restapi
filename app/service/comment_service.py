from typing import List

from sqlalchemy.orm import Session

from app.domain.models.comment import Comment
from app.domain.schemas.comment import CommentCreate, CommentUpdate
from app.service.base_service import BaseService


class CommentService(BaseService[Comment, CommentCreate, CommentUpdate]):
    def __init__(self, db: Session):
        super().__init__(Comment, db)

    def get_by_post(
        self, post_id: int, skip: int = 0, limit: int = 10
    ) -> List[Comment]:
        return (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
