"""Service 계층: 비즈니스 로직. DAO 를 조합해서 결과를 만든다.

지금은 단순 조회라 로직이 거의 없지만, 계층 분리 형태를 유지한다.
"""
from pymysql.connections import Connection

from app.repositories.test_dao import TestDao


class LoginService:
    def __init__(self, conn: Connection):
        self.dao = TestDao(conn)

    def login_user(self):
        q = "select * from user where login_id = 'msblast' and login_pw = '$2b$12$aW27ya21Fn7nK8.hla8CROEI3tJfhaUqcl0xAPIVtVOcIz57cECjK';"
        return self.dao.exec_query(q)

