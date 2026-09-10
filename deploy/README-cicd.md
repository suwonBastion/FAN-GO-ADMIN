# GitHub Actions CI/CD 설정

## 흐름

```
git push (master)
   ├─ CI (ci.yml)      : 클라우드 러너에서 pip install + app import/compile 체크
   └─ Deploy (deploy.yml): SSH로 EC2 접속 → rsync 소스 전송 → pip install
                            → 서버에서 pytest (RDS 붙음) → systemctl restart → health 체크
```

파이썬은 컴파일 산출물이 없어서 CI의 "빌드" 자리에 **import/문법 검증**(`compileall` + `from app.main import app`)이 들어간다.
RDS 접속이 필요한 `tests/` 는 클라우드에서 못 돌리므로 **배포 직후 서버에서** 실행한다.

---

## 1. GitHub 저장소 만들고 푸시

```powershell
cd C:\workspaces\adminProject
# .env 가 커밋되지 않는지 먼저 확인 (.gitignore 에 있음)
git status

gh repo create adminProject --private --source=. --remote=origin --push
# gh 가 없으면: GitHub 웹에서 repo 생성 후
#   git remote add origin https://github.com/<계정>/adminProject.git
#   git push -u origin master
```

> `.env` 는 절대 커밋하지 않는다. 서버의 `~/adminProject/.env` 는 rsync `--exclude .env` 로 보존된다.

---

## 2. 배포용 SSH 키 준비

로컬에서 EC2 접속에 쓰는 `D:\team2.pem` 을 그대로 써도 되고, 배포 전용 키를 새로 만들어도 된다(권장).

전용 키 만들기:
```powershell
ssh-keygen -t ed25519 -f deploy_key -N '""' -C "github-actions"
# deploy_key(비공개), deploy_key.pub(공개) 생성됨
```

EC2에 공개키 등록 (서버에서):
```bash
cat >> ~/.ssh/authorized_keys < deploy_key.pub   # 내용 붙여넣기
```

---

## 3. GitHub Secrets 등록

저장소 → Settings → Secrets and variables → Actions → **New repository secret**

| 이름 | 값 |
|---|---|
| `EC2_HOST` | `54.180.95.40` |
| `EC2_USER` | `ec2-user` |
| `EC2_SSH_KEY` | `deploy_key`(또는 team2.pem) **파일 전체 내용**. `-----BEGIN ...` 부터 `-----END ...` 까지 |

gh CLI로:
```powershell
gh secret set EC2_HOST --body "54.180.95.40"
gh secret set EC2_USER --body "ec2-user"
gh secret set EC2_SSH_KEY < D:\team2.pem
```

---

## 4. 최초 1회: 서버 셋업

CI/CD 는 이미 `.venv` 와 systemd 서비스가 있다고 가정한다. 아직이면 `README-deploy.md` 3번(`server_setup.sh`)을 한 번 실행해 둔다.

또한 GitHub 러너가 접속하려면 EC2 보안그룹 인바운드 **22번**이 열려 있어야 한다.
(GitHub 클라우드 러너는 IP가 고정이 아니므로 테스트 중엔 `0.0.0.0/0`, 이후 self-hosted 러너 전환 또는 IP 제한 고려.)

---

## 5. 동작 확인

```powershell
git commit --allow-empty -m "ci: trigger deploy"
git push
```

GitHub 저장소 → Actions 탭에서 CI / Deploy 진행 상황 확인.
성공하면 `http://54.180.95.40:8001/docs` 갱신됨.

---

## 6. CI 통과해야만 배포되게 하려면

`deploy.yml` 의 job 을 CI 완료 후 실행되도록 바꾼다. 가장 간단한 방법은 두 워크플로를 하나로 합치거나,
`deploy.yml` 상단을 다음으로 교체:

```yaml
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [master]

jobs:
  deploy:
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    ...
```

---

## 7. 프로젝트 B 추가 시

- B 저장소에도 같은 구조의 `deploy.yml` 을 두고, `WorkingDirectory` / 포트(8002) / 서비스명만 바꾼다.
- 또는 EC2에 **self-hosted 러너 1개**를 설치해 두면 두 프로젝트 모두 SSH 없이 로컬 명령으로 배포 가능하고 RDS 테스트도 클라우드 제약 없이 돌아간다.
