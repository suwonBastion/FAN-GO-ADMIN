# adminProject 배포 가이드 (EC2 Amazon Linux 2023)

이 프로젝트는 컴파일 "빌드"가 없다. 배포 = **소스 + 의존성 목록을 서버에 올리고, 가상환경 만들고, systemd 서비스로 실행**.

- 앱 엔트리포인트: `app.main:app`
- 내부 포트: **8001** (프로젝트 B 는 8002 등 다른 포트)
- 실행: gunicorn + UvicornWorker (워커 자동 2~3개), systemd 가 관리/자동재시작
- 지금은 nginx 없이 보안그룹에서 8001 열어서 테스트, 나중에 nginx 추가

---

## 0. 준비물

- EC2 공인 IP (예: `13.125.x.x`)
- pem 키 경로 (예: `C:\Users\asia\keys\team2.pem`)
- 보안그룹: 임시로 인바운드 all 열어둔 상태 (테스트 후 22, 80, 443 만 남길 것)
- RDS: EC2→RDS 연결 마법사로 3306 이미 허용됨

아래 명령에서 `EC2_IP`, `KEY` 를 본인 값으로 바꾼다. PowerShell 기준:

```powershell
$EC2_IP = "13.125.x.x"
$KEY    = "C:\Users\asia\keys\team2.pem"
```

---

## 1. (로컬) 전송용 zip 만들기 — 불필요 파일 제외

```powershell
cd C:\workspaces\adminProject
$tmp = "$env:TEMP\adminProject_deploy"
Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
robocopy . $tmp /E /XD .venv __pycache__ .pytest_cache .idea .git /XF *.pyc | Out-Null
Compress-Archive -Path "$tmp\*" -DestinationPath "$env:TEMP\adminProject.zip" -Force
```

> `.env` 는 포함된다 (RDS 접속정보). 서버에서 그대로 쓴다.

---

## 2. (로컬) 서버로 전송

```powershell
scp -i D:\team2.pem "$env:TEMP\adminProject.zip" ec2-user@54.180.95.40:/home/ec2-user/
```

---

## 3. (서버) 압축 풀고 셋업 스크립트 실행

```powershell
ssh -i D:\team2.pem ec2-user@54.180.95.40
```

서버 안에서:

```bash
sudo dnf install -y unzip
mkdir -p ~/adminProject
unzip -o ~/adminProject.zip -d ~/adminProject
cd ~/adminProject
chmod +x deploy/*.sh
./deploy/server_setup.sh
```

`server_setup.sh` 가 하는 일:
1. Python 3.11 설치
2. `.venv` 생성 + `requirements.txt` 설치
3. `.env` 존재 확인
4. **RDS 연결 스모크 테스트** (`SELECT 1`)
5. systemd 서비스 등록 + 시작 (`adminproject`)
6. `curl http://127.0.0.1:8001/health` 확인

---

## 4. 외부 접속 확인

브라우저에서:

```
http://<EC2_IP>:8001/health
http://<EC2_IP>:8001/docs
```

안 되면 → EC2 보안그룹 인바운드에 8001 열렸는지 확인.

---

## 5. 운영 명령어 (서버에서)

```bash
sudo systemctl status adminproject      # 상태
sudo journalctl -u adminproject -f      # 실시간 로그
sudo systemctl restart adminproject     # 재시작
```

## 6. 코드 수정 후 재배포

로컬에서 1~2번 다시 실행(zip 새로 만들어 전송) 후, 서버에서:

```bash
cd ~/adminProject && unzip -o ~/adminProject.zip -d ~/adminProject
./deploy/redeploy.sh
```

---

## 7. RDS 연결이 실패하면 (스모크 테스트 3단계에서 멈춤)

- RDS 보안그룹 인바운드에 **EC2 의 보안그룹**(또는 EC2 프라이빗 IP/서브넷)에서 3306 허용됐는지 확인
- RDS 와 EC2 가 같은 VPC 인지 확인
- `.env` 의 `DB_HOST` 가 RDS 엔드포인트와 일치하는지 확인
- 서버에서 직접 테스트: `nc -zv <RDS엔드포인트> 3306`

---

## 8. 나중에 nginx 붙이기 (프로젝트 2개 경로 분기)

```bash
sudo dnf install -y nginx
sudo cp deploy/nginx-adminproject.conf.sample /etc/nginx/conf.d/adminproject.conf
sudo nginx -t && sudo systemctl enable --now nginx
```

- `http://<EC2_IP>/admin/` → 이 프로젝트 (8001)
- `http://<EC2_IP>/b/` → 프로젝트 B (8002)
- 그다음 보안그룹에서 8001/8002 는 닫고 80(443) 만 유지
