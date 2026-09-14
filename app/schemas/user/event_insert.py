"""요청/응답 DTO (Spring 의 DTO / VO 에 해당).

ORM 모델(app.models.User)은 DB 구조, 스키마(여기)는 API 입출력 형태.
둘을 분리해야 login_pw 같은 민감 필드가 응답에 안 새어나간다.
"""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

class NEWEVENT(BaseModel):
    event_nm: str | None = None
    start_dt: str | None = None
    end_dt: str | None = None
    add: str | None = None
    event_desc: str | None = None
    event_dtl: str | None = None
    event_lat: str | None = None
    event_lon: str | None = None
    op_status_no: int | None = None
    ctg_no: int | None = None
    artist_no: int | None = None
    artist_group_no: int | None = None

class EventUpdate(BaseModel):
    event_nm: str | None = None
    start_dt: str | None = None
    end_dt: str | None = None
    add: str | None = None
    event_desc: str | None = None
    event_dtl: str | None = None
    event_lat: str | None = None
    event_lon: str | None = None
    op_status_no: int | None = None
    ctg_no: int | None = None
    artist_no: int | None = None
    artist_group_no: int | None = None