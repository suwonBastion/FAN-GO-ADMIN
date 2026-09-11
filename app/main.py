"""FastAPI 앱 엔트리포인트.

실행:
    .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload
문서:
    http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI


from app.api.user_router import router as user_router
from app.api.test_router import router as test_router
<<<<<<< HEAD
from app.api.event_router import router as event_router
=======
from app.api.cw_router import router as cw_router
>>>>>>> stage

app = FastAPI(title="Admin API")

app.include_router(user_router)
app.include_router(test_router)
<<<<<<< HEAD
app.include_router(event_router)
=======
app.include_router(cw_router)
>>>>>>> stage


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    # 파이참에서 이 파일 열고 ▶ (녹색 화살표) 누르면 이 블록이 실행됨
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
