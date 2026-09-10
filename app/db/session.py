"""SQLAlchemy Engine / Session 설정 (MySQL).

핵심:
- Engine 은 프로세스당 1개만 생성한다 (커넥션 풀을 내부에 들고 있음).
- 요청/작업 단위로 Session 을 열고 닫는다.
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# 1) Engine: 접속 정보 + 커넥션 풀. 앱 전체에서 재사용.
engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=settings.db_pool_pre_ping,
    echo=settings.db_echo,
    future=True,
)

# 2) Session 팩토리: 호출할 때마다 새 Session 인스턴스 생성.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# 3) 모든 ORM 모델의 베이스 클래스.
class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI 의존성 주입용.

    사용:
        @router.get("/users/{user_id}")
        def read_user(user_id: int, db: Session = Depends(get_db)):
            return db.get(User, user_id)
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
