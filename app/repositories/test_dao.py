"""DAO 계층: DB 접근(쿼리)만 담당. 비즈니스 규칙 없음.

SQLAlchemy 없이 pymysql 커넥션으로 직접 SQL 실행.
row 는 DictCursor 덕분에 dict 로 반환된다.
"""
from pymysql.connections import Connection


class TestDao:
    def __init__(self, conn: Connection):
        self.conn = conn

    def exec_query(self, query, params: dict | tuple | list | None = None) -> list[dict]:
        """query 실행 후 결과를 dict 리스트로 반환.

        where 절 바인딩 값은 params 로 전달한다. dict 를 넘기면
        ``%(key)s`` 플레이스홀더에, tuple/list 를 넘기면 ``%s`` 에 매핑된다.
        pymysql 이 이스케이프를 처리하므로 SQL 인젝션에 안전하다.

        예)
            dao.exec_query(
                "select * from user where user_no = %(user_no)s",
                {"user_no": 10},
            )
        """
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            return list(cur.fetchall())

    def exec_update(self, query, params: dict | tuple | list | None = None) -> int:
        """INSERT / UPDATE / DELETE / INSERT ... ON DUPLICATE KEY UPDATE 용.

        커밋까지 수행하고 영향받은 행 수를 반환한다. 예외 발생 시 롤백한다.
        바인딩 규칙은 exec_query 와 동일하다. 새로 생성된 AUTO_INCREMENT
        값이 필요하면 exec_insert 를 쓴다.

        예)
            dao.exec_update(
                "update user set nickname = %(nickname)s where user_no = %(user_no)s",
                {"nickname": "새닉", "user_no": 10},
            )
        """
        try:
            with self.conn.cursor() as cur:
                affected = cur.execute(query, params)
            self.conn.commit()
            return affected
        except Exception:
            self.conn.rollback()
            raise

    def exec_insert(self, query, params: dict | tuple | list | None = None) -> int:
        """INSERT 후 생성된 AUTO_INCREMENT PK 를 반환한다. 나머지는 exec_update 와 동일."""
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                new_id = cur.lastrowid
            self.conn.commit()
            return new_id
        except Exception:
            self.conn.rollback()
            raise
