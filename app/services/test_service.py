"""Service 계층: 비즈니스 로직. DAO 를 조합해서 결과를 만든다.

지금은 단순 조회라 로직이 거의 없지만, 계층 분리 형태를 유지한다.
"""
from pymysql.connections import Connection

from app.repositories.test_dao import TestDao


class TestService:
    def __init__(self, conn: Connection):
        self.dao = TestDao(conn)

    def select_users(self):
        q = "SELECT * FROM user;"
        return self.dao.exec_query(q)

    def select_user(self, params: dict):
        q = "SELECT * FROM user WHERE login_id = %(login_id)s and nickname = %(nickname)s;"
        return self.dao.exec_query(q, params)

    def insert_user_status(self, user_status):
        q = "INSERT INTO user_status (status_nm) values (%(status_nm)s);"
        return {"rowid": self.dao.exec_insert(q, user_status.model_dump()), "msg": "success"}

    def delete_user_status(self, status_no):
        q = "DELETE FROM user_status WHERE status_no = %(status_no)s;"
        res = self.dao.exec_update(q, {"status_no": status_no})
        return {"rowcount": res, "msg": "success"}
