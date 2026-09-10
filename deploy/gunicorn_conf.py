"""Gunicorn 설정. adminProject (이 프로젝트) 전용.

프로젝트 B 를 배포할 땐 이 파일을 복사해서 bind 포트만 8002 등으로 바꾼다.
"""
import multiprocessing

# nginx(또는 임시로 보안그룹)에서 이 포트로 프록시한다.
bind = "0.0.0.0:8001"

# 워커(프로세스) 수. t2/t3.micro(1코어)면 2 정도로 충분.
# CPU 코어가 많으면 (2 * cores) + 1 까지 늘려도 된다.
workers = min(multiprocessing.cpu_count() * 2 + 1, 3)
worker_class = "uvicorn.workers.UvicornWorker"

timeout = 60
graceful_timeout = 30
keepalive = 5

accesslog = "-"   # stdout -> journald
errorlog = "-"
loglevel = "info"
