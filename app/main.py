"""FastAPI 앱 엔트리포인트.

실행:
    .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload
문서:
    http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import yj_dashboard_router
from app.api.user_router import router as user_router
from app.api.test_router import router as test_router

from app.api.event_router import router as event_router

from app.api.cw_router import router as cw_router
from app.api.yj_login_router import router as yj_login_router
from app.api.yj_dashboard_router import router as yj_dashboard_router
from app.api.yj_eventlist_router import router as yj_eventlist_router
from app.api.event_router import router as event_router
from app.api.yj_user_router import router as yj_user_router
from app.api.yj_ctg_router import router as yj_ctg_router
from app.api.yj_artist_router import router as yj_artist_router
from app.api.yj_eventstatus_router import router as yj_eventstatus_router

app = FastAPI(title="Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://ec2-54-180-95-40.ap-northeast-2.compute.amazonaws.com:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(test_router)

app.include_router(event_router)

app.include_router(cw_router)
app.include_router(event_router)
app.include_router(yj_login_router)
app.include_router(yj_eventlist_router)
app.include_router(yj_dashboard_router)
app.include_router(yj_user_router)
app.include_router(yj_ctg_router)
app.include_router(yj_artist_router)
app.include_router(yj_eventstatus_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    # 파이참에서 이 파일 열고 ▶ (녹색 화살표) 누르면 이 블록이 실행됨
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True)
