from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domain.models.comment import Comment
from app.domain.schemas.comment import (CommentCreate, CommentRead,
                                        CommentUpdate)


class CommentService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, comment_create: CommentCreate) -> CommentRead:
        comment = Comment(**comment_create.dict())
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return CommentRead.from_orm(comment)

    def get(self, comment_id: int) -> Optional[CommentRead]:
        comment = self._get_comment_by_id(comment_id)
        return CommentRead.from_orm(comment)

    def get_multi(self, skip: int = 0, limit: int = 10) -> List[CommentRead]:
        comments = self.db.query(Comment).offset(skip).limit(limit).all()
        return [CommentRead.from_orm(comment) for comment in comments]

    def get_by_post(
        self, post_id: int, skip: int = 0, limit: int = 10
    ) -> List[CommentRead]:
        comments = (
            self.db.query(Comment)
            .filter(Comment.post_id == post_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [CommentRead.from_orm(comment) for comment in comments]

    def update(self, comment_id: int, comment_update: CommentUpdate) -> CommentRead:
        comment = self._get_comment_by_id(comment_id)
        for key, value in comment_update.dict(exclude_unset=True).items():
            setattr(comment, key, value)
        self.db.commit()
        self.db.refresh(comment)
        return CommentRead.from_orm(comment)

    def delete(self, comment_id: int) -> bool:
        comment = self._get_comment_by_id(comment_id)
        self.db.delete(comment)
        self.db.commit()
        return True

    def _get_comment_by_id(self, comment_id: int) -> Comment:
        comment = self.db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="댓글이 없습니다."
            )
        return comment
