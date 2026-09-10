"""SQLAlchemy 를 쓰지 않는 raw 커넥션 헬퍼 (pymysql).

- ORM/세션 없이 순수 DB-API 커넥션만 제공한다.
- DictCursor: row 가 {컬럼명: 값} dict 로 나온다.
- FastAPI 의존성으로 주입해서 요청 단위로 열고 닫는다.
"""
from collections.abc import Generator

import pymysql
from pymysql.connections import Connection

from app.core.config import get_settings


def _connect() -> Connection:
    s = get_settings()
    return pymysql.connect(
        host=s.db_host,
        port=s.db_port,
        user=s.db_user,
        password=s.db_password,
        database=s.db_name,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def get_conn() -> Generator[Connection, None, None]:
    """FastAPI 의존성 주입용. get_db 의 raw 버전."""
    conn = _connect()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
