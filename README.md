# 아이젠하워 매트릭스 AI 투두 앱

## 프로젝트 개요

**아이젠하워 매트릭스 AI 투두 앱**은 AI 기반 자동 분류 기능을 갖춘 현대적인 할일 관리 애플리케이션입니다. 사용자가 입력한 할일을 AI가 자동으로 긴급도(Urgency)와 중요도(Importance)로 분석하여 아이젠하워 매트릭스의 4개 사분면에 분류합니다.

### 핵심 기능
- **AI 자동 분류**: vLLM 기반 Qwen 모델을 활용한 한국어 할일 분석
- **아이젠하워 매트릭스**: 4개 사분면(DO, PLAN, DELEGATE, ELIMINATE)으로 우선순위 관리
- **실시간 동기화**: 드래그 앤 드롭으로 사분면 간 이동 가능
- **할일 편집**: 인라인 제목 편집 및 완료 표시
- **사용자 인증**: JWT 기반 회원가입/로그인

---

## 기술 스택

### Frontend
- **SvelteKit 2.x** + **Svelte 5** (Runes 기반 반응형 상태 관리)
- **Tailwind CSS 4** (유틸리티 기반 스타일링)
- **TypeScript** (엄격한 타입 체크)
- **svelte-dnd-action** (드래그 앤 드롭)

### Backend
- **FastAPI** (Python 3.13, 비동기 웹 프레임워크)
- **Pydantic** (데이터 검증 및 직렬화)
- **PyJWT** (JWT 토큰 기반 인증)
- **boto3** (AWS DynamoDB 클라이언트)

### Database
- **DynamoDB Local** (개발 환경 로컬 DynamoDB)
- **Single-Table Design** (PK/SK 기반 효율적인 쿼리)
- **GSI1** (사분면별 필터링 지원)

### AI Service
- **vLLM** (OpenAI 호환 API)
- **Qwen/Qwen3.5-9B** (한국어 이해 능력 우수)

### DevOps
- **Docker Compose** (멀티 컨테이너 오케스트레이션)
- **GitHub Actions** (CI/CD 파이프라인)

---

## 기술 선택 근거

### SvelteKit vs React
| 항목 | SvelteKit | React |
|------|-----------|-------|
| **번들 크기** | ~30KB | ~40KB+ |
| **학습 곡선** | 낮음 (HTML 기반) | 높음 (JSX 학습 필요) |
| **Svelte 5 Runes** | 네이티브 반응형 상태 (`$state`, `$derived`) | Hook 기반 (useEffect, useState) |
| **개발 경험** | 더 직관적 | 더 복잡한 상태 관리 |
| **성능** | 컴파일 타임 최적화 | 런타임 최적화 |

**선택 이유**: Svelte 5의 Runes는 React Hook보다 더 명확한 반응형 상태 관리를 제공하며, 번들 크기가 작아 빠른 로딩 시간을 보장합니다.

### FastAPI vs Express
| 항목 | FastAPI | Express |
|------|---------|---------|
| **타입 안정성** | Pydantic 기반 자동 검증 | 수동 검증 필요 |
| **비동기 지원** | 네이티브 async/await | 콜백 기반 |
| **자동 문서화** | Swagger UI 자동 생성 | 수동 작성 필요 |
| **성능** | 높음 (uvicorn) | 중간 |
| **개발 속도** | 빠름 (자동 검증) | 느림 (수동 검증) |

**선택 이유**: FastAPI는 Python의 타입 힌트를 활용한 자동 검증과 Swagger 문서화로 개발 속도를 높이고, 비동기 처리로 높은 동시성을 지원합니다.

### DynamoDB vs MongoDB
| 항목 | DynamoDB | MongoDB |
|------|----------|---------|
| **스키마** | Single-Table Design (효율적) | 다중 컬렉션 (유연함) |
| **쿼리** | PK/SK 기반 (빠름) | 복잡한 쿼리 지원 |
| **AWS 생태계** | 네이티브 통합 | 별도 설정 |
| **개발 환경** | DynamoDB Local 지원 | MongoDB Community 필요 |
| **비용** | 종량제 (프로덕션) | 무료 (Community) |

**선택 이유**: Single-Table Design으로 쿼리 성능을 최적화하고, AWS 생태계와의 네이티브 통합으로 프로덕션 배포 시 확장성을 보장합니다.

---

## 실행 방법

### 1단계: 저장소 클론
```bash
git clone https://github.com/your-org/se_mini1_todo_list.git
cd se_mini1_todo_list
```

### 2단계: 환경 변수 설정

#### Backend 환경 변수 (`.env`)
```bash
# DynamoDB 설정
DYNAMODB_ENDPOINT_URL=http://localhost:8000
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=dummy
AWS_SECRET_ACCESS_KEY=dummy

# 애플리케이션 보안
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI 서비스 설정
AI_BASE_URL=https://air.changwon.ac.kr/simon/v1
AI_MODEL=Qwen/Qwen3.5-9B
AI_TIMEOUT=10

# CORS 설정
ALLOWED_ORIGINS=["http://localhost:5173"]

# 데이터베이스
DYNAMODB_TABLE_NAME=eisenhower-tasks
```

**참고**: `.env.example` 파일을 참고하여 작성하세요.

#### Frontend 환경 변수
Docker Compose에서 자동으로 설정됩니다:
- `VITE_API_URL=http://localhost:8080/api/v1`

### 3단계: Docker Compose 실행
```bash
docker compose up -d
```

**서비스 시작 순서**:
1. DynamoDB Local (포트 8000)
2. Backend (포트 8080) - DynamoDB 헬스체크 대기
3. Frontend (포트 5173)
4. DynamoDB Admin (포트 8001)

### 4단계: 애플리케이션 접속
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8080/api/v1
- **Swagger 문서**: http://localhost:8080/docs
- **DynamoDB Admin**: http://localhost:8001

---

## 프로젝트 구조

```
se_mini1_todo_list/
├── frontend/                          # SvelteKit 프론트엔드
│   ├── src/
│   │   ├── routes/
│   │   │   ├── +layout.svelte        # 레이아웃 (헤더, 인증 가드)
│   │   │   ├── +page.svelte          # 메인 페이지 (매트릭스)
│   │   │   ├── login/+page.svelte    # 로그인 페이지
│   │   │   └── register/+page.svelte # 회원가입 페이지
│   │   ├── lib/
│   │   │   ├── types.ts              # TypeScript 타입 정의
│   │   │   ├── api/
│   │   │   │   └── client.ts         # API 클라이언트 (fetch 래퍼)
│   │   │   ├── stores/
│   │   │   │   ├── auth.svelte.ts    # 인증 상태 관리
│   │   │   │   └── tasks.svelte.ts   # 할일 상태 관리
│   │   │   └── components/
│   │   │       ├── Matrix.svelte     # 아이젠하워 매트릭스
│   │   │       ├── Quadrant.svelte   # 사분면 컴포넌트
│   │   │       ├── TaskCard.svelte   # 할일 카드
│   │   │       ├── TaskInput.svelte  # 할일 입력 필드
│   │   │       ├── ErrorMessage.svelte # 에러 메시지
│   │   │       ├── AnalyzingBadge.svelte # AI 분석 중 배지
│   │   │       └── EmptyQuadrant.svelte # 빈 사분면 표시
│   │   └── app.css                   # Tailwind CSS 임포트
│   ├── package.json
│   ├── vite.config.js                # Vite 설정 (ESM)
│   ├── svelte.config.js              # SvelteKit 설정
│   ├── tailwind.config.js            # Tailwind CSS 설정
│   ├── tsconfig.json                 # TypeScript 설정
│   └── Dockerfile                    # Node 20 Alpine 기반
│
├── backend/                           # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py                   # FastAPI 애플리케이션 진입점
│   │   ├── api/
│   │   │   ├── deps.py               # 의존성 주입 (get_current_user 등)
│   │   │   └── v1/
│   │   │       ├── router.py         # API v1 라우터
│   │   │       └── endpoints/
│   │   │           ├── auth.py       # 인증 엔드포인트
│   │   │           └── tasks.py      # 할일 엔드포인트
│   │   ├── models/
│   │   │   ├── user.py               # User 엔티티
│   │   │   └── task.py               # Task 엔티티
│   │   ├── schemas/
│   │   │   ├── user.py               # 사용자 요청/응답 스키마
│   │   │   └── task.py               # 할일 요청/응답 스키마
│   │   ├── services/
│   │   │   ├── auth_service.py       # 인증 비즈니스 로직
│   │   │   ├── task_service.py       # 할일 비즈니스 로직
│   │   │   └── ai_service.py         # AI 분류 서비스
│   │   ├── repositories/
│   │   │   ├── user_repository.py    # 사용자 데이터 접근
│   │   │   └── task_repository.py    # 할일 데이터 접근
│   │   └── core/
│   │       ├── config.py             # 설정 관리
│   │       ├── database.py           # DynamoDB 연결
│   │       └── exceptions.py         # 커스텀 예외
│   ├── tests/
│   │   ├── conftest.py               # pytest 픽스처
│   │   ├── test_auth.py              # 인증 서비스 테스트
│   │   ├── test_auth_api.py          # 인증 API 테스트
│   │   ├── test_repository.py        # 저장소 테스트
│   │   ├── test_ai_service.py        # AI 서비스 테스트
│   │   └── test_tasks_api.py         # 할일 API 테스트
│   ├── requirements.txt               # Python 의존성
│   ├── requirements-dev.txt           # 개발 의존성 (pytest 등)
│   ├── Dockerfile                    # Python 3.13 Slim 기반
│   └── pyproject.toml                # 프로젝트 메타데이터
│
├── docker-compose.yml                # 멀티 컨테이너 설정
├── .env.example                      # 환경 변수 템플릿
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI 파이프라인
└── README.md                         # 이 파일
```

---

## API 엔드포인트

### 인증 (Authentication)

#### 회원가입
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response: 201 Created
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### 로그인
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response: 200 OK
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

#### 현재 사용자 조회
```http
GET /api/v1/auth/me
Authorization: Bearer {access_token}

Response: 200 OK
{
  "id": "user-123",
  "email": "user@example.com"
}
```

### 할일 (Tasks)

#### 할일 생성
```http
POST /api/v1/tasks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "내일까지 보고서 작성"
}

Response: 201 Created
{
  "id": "task-123",
  "title": "내일까지 보고서 작성",
  "quadrant": "urgent_important",
  "completed": false,
  "urgency": 5,
  "importance": 5,
  "confidence": 0.95,
  "parsed_datetime": "2026-03-20T23:59:59",
  "user_override": false,
  "created_at": "2026-03-19T12:00:00",
  "due_date": null
}
```

#### 할일 목록 조회
```http
GET /api/v1/tasks
Authorization: Bearer {access_token}

Response: 200 OK
[
  {
    "id": "task-123",
    "title": "내일까지 보고서 작성",
    "quadrant": "urgent_important",
    "completed": false,
    "urgency": 5,
    "importance": 5,
    "confidence": 0.95,
    "parsed_datetime": "2026-03-20T23:59:59",
    "user_override": false,
    "created_at": "2026-03-19T12:00:00",
    "due_date": null
  }
]
```

#### 할일 상세 조회
```http
GET /api/v1/tasks/{task_id}
Authorization: Bearer {access_token}

Response: 200 OK
{
  "id": "task-123",
  "title": "내일까지 보고서 작성",
  "quadrant": "urgent_important",
  "completed": false,
  "urgency": 5,
  "importance": 5,
  "confidence": 0.95,
  "parsed_datetime": "2026-03-20T23:59:59",
  "user_override": false,
  "created_at": "2026-03-19T12:00:00",
  "due_date": null
}
```

#### 할일 수정
```http
PATCH /api/v1/tasks/{task_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "내일까지 보고서 작성 및 검토",
  "completed": false,
  "quadrant": "not_urgent_important",
  "user_override": true
}

Response: 200 OK
{
  "id": "task-123",
  "title": "내일까지 보고서 작성 및 검토",
  "quadrant": "not_urgent_important",
  "completed": false,
  "urgency": 3,
  "importance": 5,
  "confidence": 0.92,
  "parsed_datetime": "2026-03-20T23:59:59",
  "user_override": true,
  "created_at": "2026-03-19T12:00:00",
  "due_date": null
}
```

#### 할일 삭제
```http
DELETE /api/v1/tasks/{task_id}
Authorization: Bearer {access_token}

Response: 204 No Content
```

### 사분면 값 (Quadrant Values)
- `urgent_important` (DO): 긴급하고 중요함
- `not_urgent_important` (PLAN): 긴급하지 않지만 중요함
- `urgent_not_important` (DELEGATE): 긴급하지만 중요하지 않음
- `not_urgent_not_important` (ELIMINATE): 긴급하지도 중요하지도 않음

---

## 테스트 실행

### Backend 테스트 (pytest)
```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v
```

**테스트 커버리지**:
- ✅ 인증 서비스 (회원가입, 로그인, 토큰 검증)
- ✅ 할일 저장소 (CRUD, 사분면 필터링)
- ✅ AI 서비스 (분류, 한국어 파싱, 폴백)
- ✅ 인증 API (엔드포인트, CORS, 에러 처리)
- ✅ 할일 API (생성, 조회, 수정, 삭제, 인증)

**예상 결과**: 22개 테스트 모두 통과

### Frontend 타입 체크
```bash
cd frontend
npm install
npm run check
```

**검사 항목**:
- TypeScript 엄격 모드 검증
- Svelte 컴포넌트 타입 체크
- 미사용 변수 감지

---

## AI 사용 문서

### AI 분류 시스템 개요

이 프로젝트는 **vLLM 기반 Qwen 모델**을 활용하여 사용자의 할일을 자동으로 분석하고 아이젠하워 매트릭스의 4개 사분면으로 분류합니다.

### AI 서비스 구성

#### 엔드포인트
```
https://air.changwon.ac.kr/simon/v1
```

#### 모델
```
Qwen/Qwen3.5-9B
```

#### 주요 특징
- **한국어 지원**: 한국어 할일 설명을 정확하게 이해
- **타임아웃**: 10초 (설정 가능)
- **추가 파라미터**:
  - `enable_thinking: false` (사고 과정 비활성화)
  - `top_k: 20` (상위 20개 토큰 고려)

### AI 분류 프로세스

#### 1단계: 할일 입력
사용자가 할일을 입력합니다:
```
"내일까지 보고서 작성"
```

#### 2단계: AI 분석
Backend의 `AIService.classify_task(title)` 메서드가 vLLM API를 호출합니다:

```python
# backend/app/services/ai_service.py
def classify_task(self, title: str) -> AIClassification:
    # 1. vLLM API 호출
    # 2. 한국어 텍스트 분석
    # 3. JSON 응답 파싱
    # 4. 사분면 매핑
    # 5. 신뢰도 점수 반환
```

#### 3단계: 응답 처리
AI는 다음 형식의 JSON을 반환합니다:

```json
{
  "urgency": 5,
  "importance": 5,
  "parsed_date": "2026-03-20",
  "reasoning": "내일 마감이므로 긴급하고 중요함"
}
```

**응답 필드**:
- `urgency` (1-5): 긴급도 (5 = 매우 긴급)
- `importance` (1-5): 중요도 (5 = 매우 중요)
- `parsed_date` (ISO 8601): 파싱된 마감일
- `reasoning` (문자열): 분류 근거

#### 4단계: 사분면 매핑
AI 응답을 기반으로 사분면을 결정합니다:

```python
def map_to_quadrant(urgency: int, importance: int) -> str:
    if urgency >= 3 and importance >= 3:
        return "urgent_important"      # DO
    elif urgency < 3 and importance >= 3:
        return "not_urgent_important"  # PLAN
    elif urgency >= 3 and importance < 3:
        return "urgent_not_important"  # DELEGATE
    else:
        return "not_urgent_not_important"  # ELIMINATE
```

#### 5단계: 신뢰도 점수
AI는 분류의 신뢰도를 0.0~1.0 범위로 반환합니다:
- `0.9~1.0`: 매우 높은 신뢰도
- `0.7~0.9`: 높은 신뢰도
- `0.5~0.7`: 중간 신뢰도
- `<0.5`: 낮은 신뢰도

### 한국어 날짜/시간 파싱

AI는 한국어 표현을 자동으로 파싱합니다:

| 입력 | 파싱 결과 |
|------|----------|
| "내일까지" | 2026-03-20 |
| "이번 주 금요일" | 2026-03-21 |
| "다음 달 1일" | 2026-04-01 |
| "3월 25일" | 2026-03-25 |
| "오후 3시" | 2026-03-19T15:00:00 |

### 폴백 처리

AI 분류 실패 시 안전한 기본값을 반환합니다:

```python
AIClassification(
    urgency=None,
    importance=None,
    confidence=0,
    reasoning="파싱 실패",
    parsed_datetime=None,
    quadrant=None
)
```

**실패 원인**:
- 네트워크 오류
- API 타임아웃
- JSON 파싱 오류
- 모델 오류

**사용자 경험**:
- 할일은 여전히 생성됨
- 사분면 미분류 상태로 표시
- 사용자가 수동으로 분류 가능

### 신뢰도 기반 UI 표시

Frontend는 신뢰도에 따라 다른 UI를 표시합니다:

```svelte
{#if task.confidence >= 0.8}
  <!-- 높은 신뢰도: 일반 표시 -->
  <span>{task.quadrant}</span>
{:else if task.confidence > 0}
  <!-- 낮은 신뢰도: 경고 배지 -->
  <span class="badge-warning">신뢰도 {task.confidence}</span>
{:else}
  <!-- 분류 실패: 분석 중 배지 -->
  <AnalyzingBadge />
{/if}
```

### 사용자 오버라이드

사용자가 AI 분류에 동의하지 않으면 수동으로 변경할 수 있습니다:

```javascript
// 드래그 앤 드롭으로 다른 사분면으로 이동
await taskStore.updateTask(taskId, {
  quadrant: "not_urgent_important",
  user_override: true
});
```

**`user_override` 플래그**:
- `true`: 사용자가 수동으로 분류 변경
- `false`: AI 자동 분류

### 성능 고려사항

#### 응답 시간
- 평균: ~2-3초
- 최대: 10초 (타임아웃)

#### 최적화
- 비동기 처리: 할일 생성 중 AI 분류는 백그라운드에서 진행
- 캐싱: 동일한 제목에 대한 재분류 시 캐시 활용 (향후 구현)
- 배치 처리: 여러 할일 동시 분류 (향후 구현)

### 프롬프트 엔지니어링

AI에 전달되는 프롬프트:

```python
prompt = f"""
당신은 할일 관리 전문가입니다. 다음 할일을 분석하여 긴급도(1-5)와 중요도(1-5)를 평가하세요.

할일: "{title}"

다음 JSON 형식으로 응답하세요 (마크다운 코드 블록 없이):
{{
  "urgency": <1-5>,
  "importance": <1-5>,
  "parsed_date": "<ISO 8601 날짜 또는 null>",
  "reasoning": "<분류 근거>"
}}
"""
```

### 문제 해결

#### AI가 응답하지 않음
- 네트워크 연결 확인
- vLLM 엔드포인트 상태 확인
- API 키 유효성 확인

#### 부정확한 분류
- 할일 제목을 더 구체적으로 작성
- 날짜 정보를 명확하게 포함
- 사용자 오버라이드로 수동 조정

#### 타임아웃 오류
- `AI_TIMEOUT` 값 증가 (기본값: 10초)
- 네트워크 지연 확인
- vLLM 서버 부하 확인

---

## 개발 가이드

### 로컬 개발 환경 설정

#### Backend 개발
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v
```

#### Frontend 개발
```bash
cd frontend
npm install
npm run dev
```

### 코드 스타일

#### Python (Backend)
- PEP 8 준수
- Type hints 필수
- Docstring 작성 권장

#### TypeScript/Svelte (Frontend)
- ESLint + Prettier 설정
- Strict 모드 활성화
- 컴포넌트 단위 구조

### 커밋 메시지 규칙
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드, 의존성 등 관리
```

---

---

## 문제 해결

### Docker 컨테이너 시작 실패
```bash
# 로그 확인
docker compose logs backend
docker compose logs frontend

# 컨테이너 재시작
docker compose restart

# 전체 재구성
docker compose down
docker compose up -d --build
```

### DynamoDB 연결 오류
```bash
# DynamoDB Local 상태 확인
curl http://localhost:8000

# DynamoDB Admin 접속
http://localhost:8001
```

### API 인증 오류
- 토큰 만료 확인: `/auth/me` 엔드포인트 호출
- 토큰 형식 확인: `Authorization: Bearer {token}`
- CORS 설정 확인: `ALLOWED_ORIGINS` 환경 변수

---

## 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 기여 가이드

1. Fork 저장소
2. Feature 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'feat: add amazing feature'`)
4. 브랜치 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

---

## 문의

- **이메일**: support@example.com
- **이슈 트래킹**: GitHub Issues
- **토론**: GitHub Discussions

---

## 감사의 말

- **vLLM**: 오픈소스 LLM 서빙 프레임워크
- **Qwen**: Alibaba의 고성능 언어 모델
- **SvelteKit**: 현대적인 웹 프레임워크
- **FastAPI**: 빠른 웹 API 프레임워크
- **DynamoDB**: AWS의 NoSQL 데이터베이스

---

**마지막 업데이트**: 2026년 3월 19일
