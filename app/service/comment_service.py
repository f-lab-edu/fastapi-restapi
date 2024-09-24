from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.domain.models.comment import Comment
from app.domain.schemas.comment import CommentCreate, CommentRead, CommentUpdate


class CommentService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, comment_create: CommentCreate, author_id: str) -> Comment:
        comment = Comment(
            author_id=author_id,
            post_id=comment_create.post_id,
            content=comment_create.content,
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get(self, comment_id: int) -> Comment:
        return self.db.query(Comment).filter(Comment.id == comment_id).first()

    def update(self, comment_id: int, comment_update: CommentCreate) -> Comment:
        comment = self.db.query(Comment).filter(Comment.id == comment_id).first()
        comment.content = comment_update.content
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete(self, comment_id: int):
        comment = self.db.query(Comment).filter(Comment.id == comment_id).first()
        if comment:
            self.db.delete(comment)
            self.db.commit()  # 반드시 커밋 호출

    def _get_comment_by_id(self, comment_id: int) -> Comment:
        comment = self.db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="댓글이 없습니다."
            )
        return comment

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
