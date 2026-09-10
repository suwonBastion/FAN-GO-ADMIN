"""Controller = Spring 의 @RestController. HTTP 입출력만 담당.

라우터는 얇게: 요청 받고 → service 호출 → 응답 변환. 로직 없음.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import (
    DuplicateLoginIdError,
    UserNotFoundError,
    UserService,
)

router = APIRouter(prefix="/users", tags=["users"])


# service 를 의존성으로 주입 (Spring 의 @Autowired 대응)
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/{user_no}", response_model=UserResponse)
def read_user(user_no: int, svc: UserService = Depends(get_user_service)):
    try:
        return svc.get_user(user_no)
    except UserNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")


@router.get("", response_model=list[UserResponse])
def list_users(page: int = 1, size: int = 50, svc: UserService = Depends(get_user_service)):
    return svc.list_users(page, size)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, svc: UserService = Depends(get_user_service)):
    try:
        return svc.register(payload)
    except DuplicateLoginIdError:
        raise HTTPException(status.HTTP_409_CONFLICT, "login_id already exists")


@router.patch("/{user_no}", response_model=UserResponse)
def update_user(user_no: int, payload: UserUpdate, svc: UserService = Depends(get_user_service)):
    try:
        return svc.update_profile(user_no, payload)
    except UserNotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
