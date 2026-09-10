"""user 테이블 쿼리 모듈 테스트.

실행:
    .venv\\Scripts\\python.exe -m pytest tests/test_user_query.py -v

실제 RDS(boot2)에 접속하므로 네트워크/자격증명이 필요하다.
데이터는 읽기만 하고 conftest 의 db fixture 가 롤백한다.
"""
from datetime import datetime

from sqlalchemy import bindparam, func, select, text

from app.models import User


def test_connection_and_count(db):
    total = db.scalar(select(func.count()).select_from(User))
    assert total is not None
    assert total >= 0


def test_select_limit(db):
    rows = db.scalars(select(User).limit(3)).all()
    for u in rows:
        assert isinstance(u.user_no, int)
        assert isinstance(u.login_id, str)
        assert u.nickname is not None


def test_get_by_pk(db):
    first = db.scalar(select(User).order_by(User.user_no).limit(1))
    if first is None:
        return  # 데이터 없음
    fetched = db.get(User, first.user_no)
    assert fetched is not None
    assert fetched.user_no == first.user_no


def test_filter_by_login_id(db):
    first = db.scalar(select(User).limit(1))
    if first is None:
        return
    found = db.scalar(select(User).where(User.login_id == first.login_id))
    assert found is not None
    assert found.login_id == first.login_id


def test_column_types(db):
    u = db.scalar(select(User).limit(1))
    if u is None:
        return
    assert u.phone is None or isinstance(u.phone, str)
    assert u.birth is None or hasattr(u.birth, "year")
    assert u.created_at is None or isinstance(u.created_at, datetime)

def test_select_user(db):
    """SELECT * FROM user;  ← 여러 방식 비교.

    print 출력을 보려면 -s 옵션 필요:
        python -m pytest tests/test_user_query.py::test_select_user -v -s
    """
    # (A) 전체 행 리스트로 받기  → SELECT * FROM user;
    users = db.scalars(select(User)).all()
    print(f"\n총 {len(users)}명")

    # (B) 객체 한 줄씩 출력 (User.__repr__ 사용)
    for u in users:
        print(u)

    # (C) 특정 컬럼만 보기 좋게 출력
    print("\n--- user_no / login_id / nickname ---")
    for u in users:
        print(f"{u.user_no:>3}  {u.login_id:<30}  {u.nickname}")

    # (D) 한 행의 모든 컬럼을 dict 로 출력
    if users:
        row = {c.name: getattr(users[0], c.name) for c in User.__table__.columns}
        print("\n첫 행 전체 컬럼:", row)

    # (E) 첫 행만 필요하면 scalar (LIMIT 없이 첫 결과만 반환)
    first = db.scalar(select(User))
    print("\nscalar() 결과:", first)

    assert isinstance(users, list)


def test_raw_sql(db):
    """생 SQL 문자열을 직접 실행 (text()).

        python -m pytest tests/test_user_query.py::test_raw_sql -v -s
    """
    # (1) 파라미터 없는 단순 쿼리
    result = db.execute(text("SELECT * FROM user"))
    rows = result.all()                 # list[Row]  (Row = namedtuple 비슷)
    print(f"\n{len(rows)}행")

    # Row 접근: 인덱스 / 컬럼명 / _mapping(dict)
    r0 = rows[0]
    print("인덱스:", r0[0], r0[1])
    print("컬럼명 :", r0.user_no, r0.login_id)
    print("dict   :", dict(r0._mapping))

    # (2) 바인드 파라미터 — :name 자리표시자 + 딕셔너리로 값 전달 (SQL 인젝션 방지)
    one = db.execute(
        text("SELECT user_no, login_id, nickname FROM user WHERE login_id = :lid"),
        {"lid": "msblast"},
    ).first()
    print("\n파라미터 조회:", one)                 # (8, 'msblast', '엠블래스터')
    print("mapping     :", dict(one._mapping) if one else None)

    # (3) 스칼라 하나만
    cnt = db.execute(text("SELECT COUNT(*) FROM user")).scalar()
    print("\nCOUNT(*):", cnt)

    # (4) IN 절 등 리스트 파라미터는 expanding 바인드
    stmt = text("SELECT login_id FROM user WHERE user_no IN :ids").bindparams(
        bindparam("ids", expanding=True)
    )
    ids = [r[0] for r in db.execute(stmt, {"ids": [7, 8, 9]})]
    print("\nIN 결과:", ids)

    # (5) 생 SQL 결과를 User 객체로 매핑하고 싶으면
    users = db.scalars(
        select(User).from_statement(text("SELECT * FROM user WHERE status_no = :s")),
        {"s": 1},
    ).all()
    print("\nUser 객체로:", users[:3])

    # (6) INSERT/UPDATE/DELETE 도 동일. 단 commit 필요 (여기선 conftest 가 rollback)
    # db.execute(text("UPDATE user SET nickname = :n WHERE user_no = :id"),
    #            {"n": "새닉", "id": 8})
    # db.commit()

    assert cnt >= 1
