"""Service = Spring 의 @Service. 비즈니스 로직 + 트랜잭션 경계.

- 규칙 검증(중복 아이디 등), 비밀번호 해싱, 여러 repository 조합
- commit / rollback 은 이 계층에서 결정
"""
import hashlib

from sqlalchemy.orm import Session

from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserNotFoundError(Exception):
    pass


class DuplicateLoginIdError(Exception):
    pass


def _hash_pw(raw: str) -> str:
    # 예시용. 실제로는 passlib/bcrypt 사용 권장.
    return hashlib.sha256(raw.encode()).hexdigest()


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def get_user(self, user_no: int) -> User:
        user = self.users.get(user_no)
        if user is None:
            raise UserNotFoundError(f"user_no={user_no}")
        return user

    def list_users(self, page: int = 1, size: int = 50) -> list[User]:
        return list(self.users.list(limit=size, offset=(page - 1) * size))

    def register(self, payload: UserCreate) -> User:
        # --- 비즈니스 규칙 ---
        if self.users.exists_login_id(payload.login_id):
            raise DuplicateLoginIdError(payload.login_id)

        user = User(
            login_id=payload.login_id,
            login_pw=_hash_pw(payload.login_pw),
            nickname=payload.nickname,
            nationality_no=payload.nationality_no,
            status_no=payload.status_no,
            auth_no=payload.auth_no,
            lang_no=payload.lang_no,
            phone=payload.phone,
            name=payload.name,
            gender=payload.gender,
            birth=payload.birth,
        )
        self.users.add(user)
        self.db.commit()          # ← 트랜잭션 커밋
        self.db.refresh(user)
        return user

    def update_profile(self, user_no: int, payload: UserUpdate) -> User:
        user = self.get_user(user_no)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_no: int) -> None:
        user = self.get_user(user_no)
        self.users.delete(user)
        self.db.commit()
