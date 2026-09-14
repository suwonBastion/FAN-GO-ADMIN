# FAN:GO 관리자 API 문서

`app/main.py` 에 등록된 라우터를 기준으로 현재까지 구현된 API를 정리한다.
서버 기동 시 Swagger UI(`/docs`)에서도 동일한 목록을 확인할 수 있다.

- Base URL(로컬): `http://127.0.0.1:8000` (또는 `app/main.py` 직접 실행 시 `:8001`)
- 응답 포맷: 대부분 raw SQL 결과를 그대로 반환하는 `dict` / `list[dict]` (pymysql `DictCursor`)
- 인증: 별도 세션/토큰 처리 없음 (로그인 성공 여부만 `{"msg": "OK" | "FAILED"}` 로 응답)

## 목차

- [헬스체크](#헬스체크)
- [관리자 로그인 `/adminlogin`](#관리자-로그인-adminlogin)
- [대시보드 `/adminDash`](#대시보드-admindash)
- [이벤트 `/eventList`](#이벤트-eventlist)
- [사용자 목록 `/userList`](#사용자-목록-userlist)
- [기타 참고용 라우터](#기타-참고용-라우터)

---

## 헬스체크

### `GET /health`

서버 상태 확인용.

**응답**
```json
{ "status": "ok" }
```

---

## 관리자 로그인 `/adminlogin`

파일: `app/api/yj_login_router.py` → `app/services/yj_service.py::AdminLoginService`

### `POST /adminlogin/login`

관리자 로그인 아이디/비밀번호를 `user` 테이블에서 그대로 조회해 존재 여부로 성공/실패를 판단한다.
(평문 비교이며 세션/토큰 발급은 없음 — 추후 보완 필요)

**요청 Body**
```json
{
  "login_id": "string",
  "login_pw": "string"
}
```
`LOGINPARAMS` (`app/schemas/user/admin_login.py`) — 두 필드 모두 `str | None`, 기본값 `None`.

**응답**
```json
{ "msg": "OK" }
```
또는
```json
{ "msg": "FAILED" }
```

---

## 대시보드 `/adminDash`

파일: `app/api/yj_dashboard_router.py` → `app/services/yj_service.py::DashBoardView`

### `GET /adminDash/dashboard`

관리자 대시보드 요약 통계 + 최근 14일 일일 동선(trip_route) 생성 추이.

**Query Parameters** (`DAILYVIEW`, `Depends()` 로 바인딩되어 쿼리 파라미터로 전달됨)

| 파라미터 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `days` | int | `7` | `new_users_period`, `new_routes_period` 집계 기준 최근 N일 |

> `daily_routes` 배열은 `days` 값과 무관하게 항상 최근 14일 고정.

**응답** (list 형태, 1개 row)
```json
[
  {
    "total_users": 123,
    "new_users_period": 12,
    "total_routes": 45,
    "new_routes_period": 6,
    "avg_satisfaction": 4.3,
    "response_count": 20,
    "daily_routes": [
      { "date": "2026-09-01", "count": 3 },
      { "date": "2026-09-02", "count": 5 }
    ]
  }
]
```

---

## 이벤트 `/eventList`

파일: `app/api/yj_eventlist_router.py` → `app/services/yj_service.py::EventListView / EventNEW / EventUpdate`

### `GET /eventList/eventlist`

이벤트 목록을 카테고리/운영상태/외부 리뷰 평점/아티스트(솔로·그룹) 정보와 조인해 조회.

**응답 예시**
```json
[
  {
    "event_no": 1,
    "event_nm": "팬미팅",
    "add": "서울 강남구 ...",
    "start_dt": "2026-09-01",
    "end_dt": "2026-09-03",
    "ctg_nm": "공연",
    "ctg_type_nm": "실내",
    "total_score": 4.5,
    "op_status_nm": "운영중",
    "artist_nm": "홍길동",
    "group_nm": "그룹명"
  }
]
```
`artist_nm`, `group_nm` 은 `LEFT JOIN` 이라 아티스트/그룹이 없으면 `null`.

### `POST /eventList/newevent`

이벤트 신규 등록. **주의:** `NEWEVENT` 가 `Depends()` 로 바인딩되어 있어 JSON Body가 아니라
**쿼리 파라미터**로 각 필드를 전달해야 한다 (예: `POST /eventList/newevent?event_nm=...&start_dt=...`).

**파라미터** (`NEWEVENT`, `app/schemas/user/event_insert.py`, 전부 optional)

| 필드 | 타입 |
|---|---|
| `event_nm` | str |
| `start_dt` | str |
| `end_dt` | str |
| `add` | str |
| `event_desc` | str |
| `event_dtl` | str |
| `event_lat` | str |
| `event_lon` | str |
| `op_status_no` | int |
| `ctg_no` | int |
| `artist_no` | int |
| `artist_group_no` | int |

**응답**
```json
{ "event_no": 15 }
```
새로 생성된 `event.event_no` (AUTO_INCREMENT) 를 반환.

### `PATCH /eventList/{event_no}`

이벤트 부분 수정. 이쪽은 `Depends()` 가 아니므로 **JSON Body** 로 전달한다.

**Path Parameter**

| 이름 | 타입 | 설명 |
|---|---|---|
| `event_no` | int | 수정할 이벤트 PK |

**요청 Body** (`EventUpdate`, 전부 optional — 값이 있는 필드만 `SET` 됨)
```json
{
  "event_nm": "string",
  "start_dt": "string",
  "end_dt": "string",
  "add": "string",
  "event_desc": "string",
  "event_dtl": "string",
  "event_lat": "string",
  "event_lon": "string",
  "op_status_no": 0,
  "ctg_no": 0,
  "artist_no": 0,
  "artist_group_no": 0
}
```

**응답**
```json
{ "updated_rows": 1 }
```
Body가 전부 `null` / 비어있으면 아래처럼 응답하고 UPDATE 쿼리를 실행하지 않는다.
```json
{ "msg": "변경할 값이 없습니다" }
```

---

## 사용자 목록 `/userList`

파일: `app/api/yj_user_router.py` → `app/services/yj_service.py::USerListView / USerViewTotal`

### `GET /userList/userlist`

사용자별 기본 정보 + 언어/국적 + 관심 그룹(favorite_group) + 여행 동선(trip_route) 개수 집계.

**응답 예시**
```json
[
  {
    "user_no": 1,
    "nickname": "닉네임",
    "login_id": "id123",
    "lang_nm": "한국어",
    "nationality_nm": "대한민국",
    "favorite_group_nos": "1,3,5",
    "created_at": "2026-08-01T12:00:00",
    "trip_route_cnt": 4
  }
]
```
`favorite_group_nos` 는 `GROUP_CONCAT` 결과 문자열(콤마 구분)이며 없으면 `null`.

### `GET /userList/usertotal`

사용자 현황 요약 통계 (대시보드 상단 카드용).

**응답** (list 형태, 1개 row)
```json
[
  {
    "total_users": 123,
    "nationality_pct": 78.5,
    "trip_users": 60,
    "real_trip_pct": 48.8,
    "admin": 3
  }
]
```
- `nationality_pct`: 국적이 국내(30번)가 아닌 사용자 비율(%)
- `trip_users`: 여행(trip)을 1개 이상 만든 사용자 수
- `real_trip_pct`: 전체 사용자 대비 `trip_users` 비율(%)
- `admin`: `auth_no` 가 2/3/4(관리자 권한)인 사용자 수

---

## 기타 참고용 라우터

아래는 초기 세팅/레퍼런스용으로 남아있는 라우터로, 신규 기능 개발과는 무관하다.

| Prefix | 파일 | 설명 |
|---|---|---|
| `/users` | `app/api/user_router.py` | SQLAlchemy ORM 기반 CRUD 레퍼런스 (`GET/POST/PATCH /users`) |
| `/user` | `app/api/cw_router.py` | `GET /user/login` — 목업 로그인 |
| `/event` | `app/api/event_router.py` | `GET /event/` — 헬스체크 성격의 인사 메시지 |
| (없음) | `app/api/test_router.py` | `GET /test`, `GET /test2`, `POST /`, `DELETE /{status_no}` — raw pymysql CRUD 레퍼런스 |

---

## 변경 이력 메모

- `app/api/yj_router.py` 는 `yj_login_router` / `yj_dashboard_router` / `yj_eventlist_router` / `yj_user_router` 로 기능별 분리되며 삭제됨.
- 대시보드 `daily_routes` 는 `days` 파라미터와 무관하게 항상 최근 14일로 고정 (2026-09-14, `381b3b7`).
- 이벤트 목록에 `artist_nm`, `group_nm` 컬럼 추가 (`914418a`).
