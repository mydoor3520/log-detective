# Log Detective - 12주 학습 로드맵

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | Log Detective |
| **목표** | 실시간 에러 로그 모니터링 + AI 기반 원인 분석 Agent |
| **기간** | 12주 (8주 MVP + 4주 고도화) |
| **투자시간** | 하루 8시간 (풀타임) |
| **배포** | GCP ($300 크레딧) |
| **결과물** | CLI 기반 실행 가능한 데모 + 포트폴리오 |

---

## 학습 목표 (습득할 기술)

| 기술 | 수준 목표 |
|------|----------|
| RAG (Retrieval-Augmented Generation) | 실무 적용 가능 |
| Vector DB (Chroma) | 설계 및 최적화 |
| LangGraph/LangChain | Agent 워크플로우 설계 |
| Tool Use | 외부 도구 연동 (Git, 파일시스템) |
| 프롬프트 엔지니어링 | 분석 품질 최적화 |
| 비용/리소스 최적화 | 프로덕션 감각 |

---

## 아키텍처

```
┌────────────────────────────────────────────────────────────┐
│                    Log Detective                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  [Input Layer]                                             │
│  ├─ CLI 수동 입력 (로그 텍스트/파일)                        │
│  └─ 파일 워칭 (실시간 모니터링)                             │
│                                                            │
│  [Data Layer]                                              │
│  ├─ GitHub 레포 연동 (소스 코드)                           │
│  ├─ Vector DB - 소스 임베딩 (Chroma)                       │
│  └─ Vector DB - 에러 히스토리 (공개 데이터셋)               │
│                                                            │
│  [Processing Layer]                                        │
│  ├─ 로그 파서 (Java, Python 범용)                          │
│  ├─ 스택트레이스 추출기                                    │
│  └─ 언어 감지기                                            │
│                                                            │
│  [Agent Layer - LangGraph]                                 │
│  ├─ Tool: 파일 읽기                                        │
│  ├─ Tool: Git blame                                        │
│  ├─ Tool: RAG 검색 (소스)                                  │
│  ├─ Tool: RAG 검색 (히스토리)                              │
│  └─ 추론: 원인 분석 + 해결책 제안                          │
│                                                            │
│  [Output Layer]                                            │
│  ├─ CLI 출력 (분석 리포트)                                 │
│  └─ Slack 알림                                             │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Phase 1: MVP (Week 1-8)

### Week 1: 환경 세팅 + 로그 파서 기초

**목표:** 개발 환경 구축, 로그 파싱 기초 구현

**학습 내용:**
- [ ] Python 프로젝트 구조 (Poetry/uv)
- [ ] 로그 포맷 이해 (Java, Python 스택트레이스)
- [ ] 정규식 기반 파싱

**구현 태스크:**
- [ ] 프로젝트 초기화 (`pyproject.toml`, 폴더 구조)
- [ ] Java 로그 파서 구현
- [ ] Python 로그 파서 구현
- [ ] 언어 자동 감지 로직
- [ ] 단위 테스트 작성

**결과물:**
```bash
log-detective parse --file error.log
# Output: 파싱된 스택트레이스 JSON
```

**리소스 벤치마크:**
- [ ] 파싱 속도 측정 (1000줄 기준)
- [ ] 메모리 사용량 측정

---

### Week 2: Vector DB + 임베딩 기초

**목표:** Chroma 사용법 습득, 소스 코드 임베딩

**학습 내용:**
- [ ] 임베딩 개념 (텍스트 → 벡터)
- [ ] Chroma 기본 사용법
- [ ] 청킹 전략 (코드를 어떻게 나눌 것인가)

**구현 태스크:**
- [ ] Chroma 설치 및 기본 CRUD
- [ ] 소스 코드 청킹 로직 (파일별, 함수별)
- [ ] OpenAI 임베딩 API 연동
- [ ] 로컬 임베딩 모델 테스트 (sentence-transformers)
- [ ] 검색 테스트 (쿼리 → 관련 코드)

**결과물:**
```bash
log-detective index --repo /path/to/project
log-detective search --query "NullPointerException in UserService"
# Output: 관련 소스 코드 조각들
```

**리소스 벤치마크:**
- [ ] 임베딩 생성 시간 (파일 100개 기준)
- [ ] Vector DB 메모리 사용량
- [ ] 검색 응답 시간

---

### Week 3: GitHub 연동 + 소스 인덱싱

**목표:** GitHub 레포 클론, 자동 인덱싱 파이프라인

**학습 내용:**
- [ ] GitHub API 기초
- [ ] Git 명령어 프로그래매틱 실행
- [ ] 증분 업데이트 전략

**구현 태스크:**
- [ ] GitHub 레포 클론 기능
- [ ] 파일 변경 감지 (git diff)
- [ ] 변경된 파일만 재임베딩
- [ ] `.gitignore` 패턴 존중
- [ ] 대용량 레포 처리 (선택적 인덱싱)

**결과물:**
```bash
log-detective github sync --repo https://github.com/user/project
log-detective github status
# Output: 인덱싱 상태, 파일 수, 마지막 동기화 시간
```

**리소스 벤치마크:**
- [ ] 전체 인덱싱 시간 (중간 규모 레포)
- [ ] 증분 업데이트 시간

---

### Week 4: RAG 파이프라인 구축

**목표:** 에러 로그 → 관련 소스 검색 → 컨텍스트 구성

**학습 내용:**
- [ ] RAG 아키텍처 이해
- [ ] 검색 품질 향상 기법 (reranking, hybrid search)
- [ ] 컨텍스트 윈도우 최적화

**구현 태스크:**
- [ ] 스택트레이스 → 검색 쿼리 변환
- [ ] 관련 소스 코드 검색
- [ ] 검색 결과 reranking
- [ ] LLM용 컨텍스트 구성 (프롬프트 템플릿)
- [ ] 검색 품질 평가 (수동 테스트)

**결과물:**
```bash
log-detective analyze --error "java.lang.NullPointerException at com.example.UserService.getUser(UserService.java:42)"
# Output: 관련 소스 코드 + 컨텍스트
```

---

### Week 5: 에러 히스토리 DB 구축

**목표:** 과거 에러 + 해결책 데이터베이스 구축

**학습 내용:**
- [ ] 공개 에러 데이터셋 조사
- [ ] 데이터 전처리 및 정제
- [ ] 유사도 검색 튜닝

**데이터셋 전략 (현실적 접근):**

> ⚠️ **주의:** 공개 데이터셋 정제는 예상보다 시간이 많이 소요됩니다.

| 전략 | 우선순위 | 설명 |
|------|----------|------|
| **학습 중 축적** | 1순위 | 본인이 겪는 에러 + 해결책 직접 기록 |
| **큐레이션된 샘플** | 2순위 | 50-100개 고품질 에러-해결책 쌍 직접 작성 |
| **Stack Overflow 부분 활용** | 3순위 | 검증된 답변만 선별 (전체 크롤링 X) |

**구현 태스크:**
- [ ] 에러-해결책 스키마 정의
- [ ] 초기 샘플 데이터 50개 직접 작성
- [ ] Vector DB에 저장
- [ ] 유사 에러 검색 기능
- [ ] 검색 정확도 평가
- [ ] 학습 중 에러 자동 축적 파이프라인

**결과물:**
```bash
log-detective history search --error "Connection refused"
# Output: 유사 에러 사례 + 해결책

log-detective history add --error "<error>" --solution "<solution>"
# 새 에러-해결책 추가
```

---

### Week 6: Agent 개발 (LangGraph)

**목표:** 분석 워크플로우를 Agent로 구현

**학습 내용:**
- [ ] LangGraph 기본 개념
- [ ] Agent vs Chain 차이
- [ ] Tool 정의 및 연동
- [ ] 상태 관리

**구현 태스크:**
- [ ] Agent 상태 정의
- [ ] Tool 구현: 파일 읽기
- [ ] Tool 구현: Git blame
- [ ] Tool 구현: RAG 검색 (소스)
- [ ] Tool 구현: RAG 검색 (히스토리)
- [ ] Agent 워크플로우 정의
- [ ] 분석 결과 포맷팅

**Agent 워크플로우:**
```
1. 로그 파싱 → 에러 타입, 위치 추출
2. 관련 소스 검색 (RAG)
3. 유사 에러 검색 (RAG)
4. 추가 컨텍스트 필요 시 Tool 호출
5. 종합 분석 및 해결책 제안
```

**결과물:**
```bash
log-detective analyze --file error.log
# Output:
# [에러 요약]
# [관련 소스 코드]
# [유사 사례]
# [원인 분석]
# [해결책 제안]
```

---

### Week 7: 실시간 모니터링 + 최적화

**목표:** 파일 워칭, 리소스 최적화

**학습 내용:**
- [ ] watchdog 라이브러리
- [ ] 디바운싱, Rate limiting
- [ ] 비동기 처리 (asyncio)

**구현 태스크:**
- [ ] 파일 워칭 구현 (watchdog)
- [ ] 에러 패턴 감지 (ERROR, Exception 등)
- [ ] 디바운싱 (동일 에러 중복 방지)
- [ ] Rate limiting (초당 N건 제한)
- [ ] 비동기 분석 처리

**최적화 태스크:**
- [ ] 리소스 사용량 프로파일링
- [ ] 병목 지점 식별 및 개선
- [ ] 메모리 최적화 (Chroma persistent 모드)
- [ ] API 호출 최적화 (캐싱, 배치)

**결과물:**
```bash
log-detective watch --file /var/log/app.log
# 실시간 에러 감지 및 분석
```

**리소스 목표 (점진적 달성):**

> ⚠️ **참고:** 아래 목표는 최종 목표이며, 초기에는 달성이 어려울 수 있습니다. 점진적으로 최적화합니다.

| 지표 | 초기 허용 | 최종 목표 |
|------|----------|----------|
| 대기 시 CPU | < 5% | < 1% |
| 대기 시 메모리 | < 1GB | < 500MB |
| 에러 1건 분석 | < 30초 | < 10초 |
| 에러 1건 비용 | < $0.10 | < $0.03 |

---

### Week 8: Slack 알림 + CLI 완성

**목표:** MVP 완성, 데모 가능 상태

**학습 내용:**
- [ ] Slack Webhook API
- [ ] Click/Typer CLI 프레임워크
- [ ] 설정 파일 관리 (YAML/TOML)

**구현 태스크:**
- [ ] Slack Webhook 연동
- [ ] 알림 메시지 포맷팅
- [ ] CLI 명령어 정리 (click/typer)
- [ ] 설정 파일 (`config.yaml`)
- [ ] 에러 핸들링 및 로깅
- [ ] README 작성

**CLI 명령어 완성:**
```bash
# 설정
log-detective config init
log-detective config set github.token <token>
log-detective config set slack.webhook <url>

# 인덱싱
log-detective index --repo <path>
log-detective github sync --repo <url>

# 분석
log-detective analyze --file <log-file>
log-detective analyze --text "<error-message>"

# 모니터링
log-detective watch --file <log-file>
log-detective watch stop

# 히스토리
log-detective history search --error "<query>"
log-detective history add --error "<error>" --solution "<solution>"
```

**MVP 완료 체크리스트:**
- [ ] 수동 분석 동작
- [ ] 실시간 모니터링 동작
- [ ] Slack 알림 동작
- [ ] README 완성
- [ ] 데모 시나리오 준비

---

## Phase 2: 고도화 (Week 9-12)

### Week 9: 멀티 LLM 라우팅 + 비용 최적화

**목표:** 에러 복잡도에 따른 모델 선택

**구현 태스크:**
- [ ] 에러 복잡도 분류기
- [ ] 간단한 에러 → GPT-4o-mini / Claude Haiku
- [ ] 복잡한 에러 → GPT-4o / Claude Sonnet
- [ ] 비용 추적 대시보드
- [ ] 일일/월간 비용 제한

---

### Week 10: 추가 언어 지원 + 커스텀 포맷

**목표:** Node.js, Go 지원, 커스텀 로그 포맷

**구현 태스크:**
- [ ] Node.js 로그 파서
- [ ] Go 로그 파서
- [ ] 커스텀 정규식 패턴 지원
- [ ] 파서 플러그인 아키텍처

---

### Week 11: 웹 UI (Streamlit)

**목표:** 데모용 웹 인터페이스

**구현 태스크:**
- [ ] Streamlit 기본 UI
- [ ] 로그 입력 폼
- [ ] 분석 결과 시각화
- [ ] 실시간 모니터링 대시보드
- [ ] 히스토리 조회

---

### Week 12: GCP 배포 + 포트폴리오 정리

**목표:** 클라우드 배포, 문서화

**구현 태스크:**
- [ ] Docker 이미지 빌드
- [ ] GCP Cloud Run 배포
- [ ] 도메인 연결 (선택)
- [ ] 포트폴리오 문서 작성
- [ ] 기술 블로그 포스트 (선택)
- [ ] GitHub README 완성

---

## 리소스 관리 가이드

### 비용 예산 (3개월)

| 항목 | 예상 비용 |
|------|----------|
| GCP 크레딧 | $300 (무료) |
| OpenAI API | ~$50 |
| Claude API | ~$30 |
| 총 예상 | ~$80 (크레딧 내) |

### 리소스 최적화 전략

1. **임베딩:** 로컬 모델 우선, 품질 필요 시 API
2. **LLM:** 간단한 에러는 저렴한 모델
3. **Vector DB:** Persistent 모드로 메모리 절약
4. **캐싱:** 동일 에러 재분석 방지

---

## 위험 요소 및 대응

| 위험 | 확률 | 영향 | 대응 |
|------|------|------|------|
| RAG 검색 품질 낮음 | 중 | 높음 | 청킹 전략 조정, reranking 추가 |
| Agent 추론 불안정 | 중 | 중 | 프롬프트 튜닝, fallback 로직 |
| 리소스 초과 | 낮음 | 중 | 벤치마크 기반 최적화 |
| 에러 데이터 품질 | 중 | 중 | 직접 큐레이션 우선, 점진적 축적 |
| GCP 크레딧 소진 | 낮음 | 높음 | 비용 모니터링, 알림 설정 |

---

## 성공 기준

### MVP (Week 8)

- [ ] CLI로 에러 로그 분석 가능
- [ ] GitHub 레포 연동 동작
- [ ] 실시간 모니터링 동작
- [ ] Slack 알림 동작
- [ ] 분석 품질: 10개 테스트 케이스 중 7개 이상 유용한 결과

### 최종 (Week 12)

- [ ] 웹 UI 데모 가능
- [ ] GCP 배포 완료
- [ ] 포트폴리오 문서 완성
- [ ] 면접 데모 시나리오 준비

---

## 폴더 구조

```
log-detective/
├── .sisyphus/
│   └── plans/
│       └── log-detective-roadmap.md
├── src/
│   ├── __init__.py
│   ├── cli.py                 # CLI 진입점
│   ├── config.py              # 설정 관리
│   ├── parsers/               # 로그 파서
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── java.py
│   │   └── python.py
│   ├── indexer/               # 소스 인덱싱
│   │   ├── __init__.py
│   │   ├── github.py
│   │   └── embedder.py
│   ├── rag/                   # RAG 파이프라인
│   │   ├── __init__.py
│   │   ├── retriever.py
│   │   └── reranker.py
│   ├── agent/                 # 분석 Agent
│   │   ├── __init__.py
│   │   ├── graph.py
│   │   └── tools.py
│   ├── monitor/               # 실시간 모니터링
│   │   ├── __init__.py
│   │   └── watcher.py
│   └── notifier/              # 알림
│       ├── __init__.py
│       └── slack.py
├── tests/
├── data/
│   └── error_history/         # 에러 히스토리 데이터
├── pyproject.toml
├── README.md
└── config.example.yaml
```

---

## 다음 단계

1. `/sisyphus` 명령으로 Week 1 태스크 시작
2. 매주 금요일 진행 상황 리뷰
3. 문제 발생 시 계획 조정

---

*Plan created by Prometheus*
*Last updated: 2025-01-27*
*Reviewed by: Gemini (Cross-LLM Review)*
