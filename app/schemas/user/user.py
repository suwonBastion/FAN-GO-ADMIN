"""요청/응답 DTO (Spring 의 DTO / VO 에 해당).

ORM 모델(app.models.User)은 DB 구조, 스키마(여기)는 API 입출력 형태.
둘을 분리해야 login_pw 같은 민감 필드가 응답에 안 새어나간다.
"""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    login_id: str
    login_pw: str
    nickname: str
    nationality_no: int
    status_no: int
    auth_no: int
    lang_no: int
    phone: str | None = None
    name: str | None = None
    gender: str | None = None
    birth: date | None = None


class UserUpdate(BaseModel):
    nickname: str | None = None
    phone: str | None = None
    name: str | None = None
    profile_img: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # ORM 객체 → 스키마 자동 변환

    user_no: int
    login_id: str
    nickname: str
    phone: str | None
    name: str | None
    gender: str | None
    birth: date | None
    created_at: datetime | None
    profile_img: str | None
    # login_pw 는 일부러 제외
