#!/usr/bin/env bash
# EC2 (Amazon Linux 2023) 에서 실행. 프로젝트 파일을 이미 전송한 상태여야 한다.
#   전송 위치: /home/ec2-user/adminProject
set -euo pipefail

APP_DIR="/home/ec2-user/adminProject"
cd "$APP_DIR"

echo "== 1. Python 3.11 설치 =="
sudo dnf install -y python3.11 python3.11-pip

echo "== 2. 가상환경 생성 & 의존성 설치 =="
python3.11 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -r requirements.txt

echo "== 3. .env 확인 =="
if [ ! -f .env ]; then
  echo "!! .env 가 없다. .env.example 을 복사해서 값을 채운 뒤 다시 실행하라." >&2
  exit 1
fi

echo "== 4. DB 연결 스모크 테스트 =="
./.venv/bin/python -c "
from sqlalchemy import text
from app.db.session import engine
with engine.connect() as c:
    print('DB OK:', c.execute(text('SELECT 1')).scalar())
"

echo "== 5. systemd 서비스 등록 =="
sudo cp deploy/adminproject.service /etc/systemd/system/adminproject.service
sudo systemctl daemon-reload
sudo systemctl enable --now adminproject
sleep 2
sudo systemctl status adminproject --no-pager || true

echo "== 6. 헬스체크 =="
curl -s http://127.0.0.1:8001/health && echo

echo
echo "완료. 임시로 보안그룹에서 8001 포트를 열면 http://<EC2-공인IP>:8001/docs 로 접속 가능."
