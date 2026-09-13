"""Service 계층: 비즈니스 로직. DAO 를 조합해서 결과를 만든다.

지금은 단순 조회라 로직이 거의 없지만, 계층 분리 형태를 유지한다.
"""
from pymysql.connections import Connection

from app.repositories.test_dao import TestDao


class AdminLoginService:
    def __init__(self, conn: Connection):
        self.dao = TestDao(conn)

    # def login_admin_user(self):
    #     q = "select * from user where login_id = {} and login_pw = {};"
    #     return self.dao.exec_query(q)

    def login_admin_user(self, datas):
        q = "select * from user where login_id = %(login_id)s and login_pw = %(login_pw)s;"
        result = self.dao.exec_query(q, datas.model_dump())

        if result:
            return {"msg" : "OK"}

        return {"msg" : "FAILED"} 


class DashBoardView:
    def __init__(self, conn: Connection):
        self.dao = TestDao(conn)

    def dash_board_view(self, datas):
        q = "SELECT (SELECT COUNT(*) FROM user) AS total_users, (SELECT COUNT(*) FROM user WHERE created_at >= CURDATE() - INTERVAL 7 DAY AND created_at < CURDATE()) AS new_users_period, (SELECT COUNT(*) FROM trip_route) AS total_routes, (SELECT COUNT(*) FROM trip_route WHERE created_at >= CURDATE() - INTERVAL 7 DAY AND created_at < CURDATE()) AS new_routes_period, (SELECT ROUND(AVG(rating), 2) FROM review WHERE rating IS NOT NULL) AS avg_satisfaction, (SELECT COUNT(*) FROM review WHERE rating IS NOT NULL) AS response_count, (WITH RECURSIVE seq AS (SELECT 1 AS n UNION ALL SELECT n + 1 FROM seq WHERE n + 1 <= 7), d AS (SELECT CURDATE() - INTERVAL n DAY AS route_date FROM seq) SELECT JSON_ARRAYAGG(JSON_OBJECT('date', d.route_date, 'count', COALESCE(r.route_count, 0))) FROM d LEFT JOIN (SELECT DATE(created_at) AS route_date, COUNT(*) AS route_count FROM trip_route WHERE created_at >= CURDATE() - INTERVAL 7 DAY AND created_at < CURDATE() GROUP BY DATE(created_at)) r ON d.route_date = r.route_date) AS daily_routes;"
        return self.dao.exec_query(q, datas.model_dump())


class EventListView:
    def __init__(self, conn: Connection):
        self.dao = TestDao(conn)

    def event_list_view(self):
        q = "select e.event_no, e.event_nm, e.add, e.start_dt, e.end_dt, c.ctg_nm, ct.ctg_type_nm, er.total_score, os.op_status_nm from event e, ctg c, ctg_type ct, external_review er, op_status os where e.ctg_no = c.ctg_no and c.ctg_type_no = ct.ctg_type_no and e.event_no = er.event_no and e.op_status_no = os.op_status_no;"
        return self.dao.exec_query(q)













