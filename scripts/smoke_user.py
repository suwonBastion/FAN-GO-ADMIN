"""user 테이블 쿼리 스모크 테스트 (pytest 불필요).

실행:
    .venv\\Scripts\\python.exe -m scripts.smoke_user
"""
from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.models import User


def main() -> None:
    with SessionLocal() as db:
        # 1) 전체 건수
        total = db.scalar(select(func.count()).select_from(User))
        print(f"user row 수: {total}")

        # 2) 최근 5명 (created_at 없으면 user_no 역순)
        rows = db.scalars(select(User).order_by(User.user_no.desc()).limit(5)).all()
        for u in rows:
            print(f"  #{u.user_no} {u.login_id} / {u.nickname} / status={u.status_no}")

        # 3) 단건 조회 (첫 번째 user)
        first = db.scalar(select(User).order_by(User.user_no).limit(1))
        if first:
            same = db.get(User, first.user_no)
            print(f"get({first.user_no}) -> {same!r}")

        # 4) login_id 로 조회
        if first:
            by_id = db.scalar(select(User).where(User.login_id == first.login_id))
            print(f"login_id={first.login_id!r} -> user_no={by_id.user_no}")

    print("OK")


if __name__ == "__main__":
    main()
