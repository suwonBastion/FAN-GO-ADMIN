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
from app.schemas.user.admin_login import LOGINPARAMS
from app.schemas.user.dashboard_views import DAILYVIEW
from app.schemas.user.event_insert import NEWEVENT, EventUpdate
from app.schemas.user.user_params import UserFilter
from app.schemas.user.user_status import UserStatusInsert
from app.services.cw_service import LoginService
from app.services.test_service import TestService
from app.services.yj_service import EventListView, EventNEW, EventUpdate as EventUpdateService

router = APIRouter(prefix="/eventList", tags=["eventList"])




def get_eventlist_view(conn: Connection = Depends(get_conn)) -> EventListView:
    return EventListView(conn)


@router.get("/eventlist")
def eventlist(
        svc: EventListView = Depends(get_eventlist_view)):
    return svc.event_list_view()



def get_event_new(conn: Connection = Depends(get_conn)) -> EventNEW:
    return EventNEW(conn)


@router.post("/newevent")
def newevent(
        datas: NEWEVENT = Depends(),
        svc: EventNEW = Depends(get_event_new)):
    return svc.event_insert_new(datas)




def get_event_update(conn: Connection = Depends(get_conn)) -> EventUpdateService:
    return EventUpdateService(conn)


@router.patch("/{event_no}")
def updateevent(
        event_no: int,
        datas: EventUpdate,
        svc: EventUpdateService = Depends(get_event_update)):
    return svc.update_event(event_no, datas)