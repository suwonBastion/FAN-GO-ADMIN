"""쿼리 파라미터용 DTO."""
from pydantic import BaseModel


class UserFilter(BaseModel):
    login_id: str
    nickname: str
