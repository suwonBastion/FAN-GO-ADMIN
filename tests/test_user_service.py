"""service 계층 테스트.

    .venv\\Scripts\\python.exe -m pytest tests/test_user_service.py -v -s
"""
from app.services.user_service import UserNotFoundError, UserService


def test_get_user(db):
    svc = UserService(db)
    user = svc.get_user(7)
    print(user)
    assert user.user_no == 7


def test_get_user_not_found(db):
    svc = UserService(db)
    try:
        svc.get_user(999999)
        raise AssertionError("예외가 나야 함")
    except UserNotFoundError as e:
        print("expected:", e)


def test_list_users(db):
    svc = UserService(db)
    users = svc.list_users(page=1, size=5)
    for u in users:
        print(u)
    assert len(users) <= 5
