from typing import List

from sqlalchemy.orm import Session

from app.domain.models.comment import Comment
from app.domain.models.post import Post
from app.domain.models.user import User
from app.domain.schemas.comment import CommentRead
from app.domain.schemas.post import PostRead
from app.domain.schemas.user import UserCreate, UserRead, UserUpdate
from app.service.base_service import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_posts_by_user(
        self, user_id: int, skip: int = 0, limit: int = 10
    ) -> List[PostRead]:
        posts = (
            self.db.query(Post)
            .filter(Post.author == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [PostRead.from_orm(post) for post in posts]

    def get_comments_by_user(
        self, user_id: int, skip: int = 0, limit: int = 10
    ) -> List[CommentRead]:
        comments = (
            self.db.query(Comment)
            .filter(Comment.author_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [CommentRead.from_orm(comment) for comment in comments]
