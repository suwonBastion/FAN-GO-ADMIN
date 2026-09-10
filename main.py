"""파이참 실행용 엔트리포인트 (프로젝트 루트).

파이참에서 이 파일을 열고 ▶ (녹색 화살표) 클릭하면 서버가 뜬다.
    http://127.0.0.1:8000/docs
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
