"""user 테이블 ORM 모델.

실제 스키마(CREATE TABLE `user`)와 1:1 매핑.
"""
from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class User(Base):
    __tablename__ = "user"

    user_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    login_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    login_pw: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))

    # --- FK 컬럼 (NOT NULL) ---
    nationality_no: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("nationality.nationality_no", name="R_39"), nullable=False, index=True
    )
    status_no: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user_status.status_no", name="R_41"), nullable=False, index=True
    )
    auth_no: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("auth.auth_no", name="R_42"), nullable=False, index=True
    )
    lang_no: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("lang.lang_no", name="R_60"), nullable=False, index=True
    )

    nickname: Mapped[str] = mapped_column(String(50), nullable=False)

    # --- nullable 프로필 정보 ---
    name: Mapped[str | None] = mapped_column(String(50))
    gender: Mapped[str | None] = mapped_column(String(10))
    birth: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    profile_img: Mapped[str | None] = mapped_column(String(255))

    # --- 관계 (참조 테이블 모델이 생기면 주석 해제) ---
    # nationality: Mapped["Nationality"] = relationship(lazy="joined")
    # status: Mapped["UserStatus"] = relationship(lazy="joined")
    # auth: Mapped["Auth"] = relationship(lazy="joined")
    # lang: Mapped["Lang"] = relationship(lazy="joined")

    def __repr__(self) -> str:
        return f"<User user_no={self.user_no} login_id={self.login_id!r}>"
