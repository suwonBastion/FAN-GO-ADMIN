"""Repository = Spring 의 @Repository / DAO 계층.

DB 접근(쿼리)만 담당. 비즈니스 규칙은 여기 두지 않는다.
"""
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, user_no: int) -> User | None:
        return self.db.get(User, user_no)

    def get_by_login_id(self, login_id: str) -> User | None:
        return self.db.scalar(select(User).where(User.login_id == login_id))

    def list(self, limit: int = 50, offset: int = 0) -> Sequence[User]:
        return self.db.scalars(
            select(User).order_by(User.user_no.desc()).limit(limit).offset(offset)
        ).all()

    def exists_login_id(self, login_id: str) -> bool:
        return self.db.scalar(select(User.user_no).where(User.login_id == login_id)) is not None

    def add(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()      # user_no 채번 (commit 은 service 가 담당)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
