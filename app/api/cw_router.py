"""Controller: HTTP 입출력만 담당. 요청 받고 → service 호출 → 응답.

SQLAlchemy 를 쓰지 않고 pymysql raw 커넥션 + DictCursor 로
결과를 dict 리스트 그대로 return 하는 레퍼런스.

호출:
    GET http://127.0.0.1:8000/test
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pymysql.connections import Connection

from app.db.raw import get_conn
from app.schemas.user.user_params import UserFilter
from app.schemas.user.user_status import UserStatusInsert
from app.services.cw_service import LoginService
from app.services.test_service import TestService

router = APIRouter(prefix="/user", tags=["user"])


def get_cw_service(conn: Connection = Depends(get_conn)) -> LoginService:
    return LoginService(conn)


@router.get("/login")
def login(svc: LoginService = Depends(get_cw_service)):
    return svc.login_user()

