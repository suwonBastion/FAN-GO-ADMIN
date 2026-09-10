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
from app.services.test_service import TestService

router = APIRouter(tags=["test"])


def get_test_service(conn: Connection = Depends(get_conn)) -> TestService:
    return TestService(conn)


@router.get("/test")
def test(svc: TestService = Depends(get_test_service)):
    return svc.select_users()

@router.get("/test2")
def test2(
    f: UserFilter = Depends(),
    svc: TestService = Depends(get_test_service),
):
    return svc.select_user(f.model_dump())

@router.post("/")
def p_test(
        user_status: UserStatusInsert,
        svc: TestService = Depends(get_test_service),
):
    return svc.insert_user_status(user_status)

@router.delete("/{status_no}")
def d_test(
        status_no: int,
        svc: TestService = Depends(get_test_service),
):
    return svc.delete_user_status(status_no)