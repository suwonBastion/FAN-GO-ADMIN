import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal


@pytest.fixture
def db() -> Session:
    """읽기 전용 테스트용 세션. 테스트가 끝나면 롤백해 DB를 건드리지 않는다."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
