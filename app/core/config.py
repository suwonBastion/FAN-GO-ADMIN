"""환경 설정 로더.

.env 파일이나 OS 환경변수에서 DB 접속 정보를 읽어온다.
pydantic-settings 사용: pip install pydantic-settings
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- MySQL 접속 정보 ---
    db_host: str = Field(default="localhost")
    db_port: int = Field(default=3306)
    db_user: str = Field(default="admin")
    db_password: str = Field(default="")
    db_name: str = Field(default="boot2")

    # --- 커넥션 풀 튜닝 ---
    db_pool_size: int = Field(default=10)          # 상시 유지 커넥션 수
    db_max_overflow: int = Field(default=20)       # 풀 초과 시 추가 허용치
    db_pool_recycle: int = Field(default=1800)     # 초. MySQL wait_timeout(기본 8h)보다 짧게
    db_pool_pre_ping: bool = Field(default=True)   # 사용 전 커넥션 유효성 확인
    db_echo: bool = Field(default=False)           # True면 실행 SQL 로그 출력

    @property
    def database_url(self) -> str:
        # 드라이버: PyMySQL (순수 파이썬, 설치 간단)
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
