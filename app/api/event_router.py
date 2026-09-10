from fastapi import APIRouter, Depends, Query
from pymysql.connections import Connection

from app.db.raw import get_conn
from app.schemas.user.user_params import UserFilter
from app.schemas.user.user_status import UserStatusInsert
from app.services.test_service import TestService

router = APIRouter(prefix="/event", tags=["장소"])


def get_test_service(conn: Connection = Depends(get_conn)) -> TestService:
    return TestService(conn)

@router.get("/")
def test(svc: TestService = Depends(get_test_service)):
    return {"message":"안녕"}


