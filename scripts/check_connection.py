"""DB 연결 확인용 스크립트.

실행:
    .venv\\Scripts\\python.exe -m scripts.check_connection
"""
from sqlalchemy import create_engine, inspect, text

from app.core.config import get_settings

settings = get_settings()


def main() -> None:
    # DB 이름 없이 서버에만 접속해서 사용 가능한 스키마 확인
    server_url = (
        f"mysql+pymysql://{settings.db_user}:{settings.db_password}"
        f"@{settings.db_host}:{settings.db_port}/?charset=utf8mb4"
    )
    engine = create_engine(server_url)
    with engine.connect() as conn:
        version = conn.execute(text("SELECT VERSION()")).scalar_one()
        print(f"[OK] MySQL 연결 성공 - 버전: {version}")
        print("사용 가능한 데이터베이스:")
        for (name,) in conn.execute(text("SHOW DATABASES")):
            print(f"  - {name}")

    # 현재 설정된 DB의 테이블 목록
    try:
        db_engine = create_engine(settings.database_url)
        with db_engine.connect():
            pass
        tables = inspect(db_engine).get_table_names()
        print(f"\n[{settings.db_name}] 테이블 {len(tables)}개:")
        for t in tables:
            print(f"  - {t}")
    except Exception as e:  # noqa: BLE001
        print(f"\n[WARN] '{settings.db_name}' 접속 실패: {e}")


if __name__ == "__main__":
    main()
