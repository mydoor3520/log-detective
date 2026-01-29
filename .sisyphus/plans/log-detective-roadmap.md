# Log Detective - 10주 학습 로드맵 (Revised)

> **Revision Note:** Momus 검토 피드백 반영 (2025-01-27)
> - MVP 8주 → 10주로 확장 (버퍼 포함)
> - 테스트 케이스 10개 사전 정의
> - 에러-해결책 스키마 명시
> - LangGraph vs Chain 결정 포인트 추가
> - Phase 2 범위 축소

---

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | Log Detective |
| **목표** | 실시간 에러 로그 모니터링 + AI 기반 원인 분석 Agent |
| **기간** | 14주 (10주 MVP + 4주 고도화) |
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
│  └─ Vector DB - 에러 히스토리                              │
│                                                            │
│  [Processing Layer]                                        │
│  ├─ 로그 파서 (Java, Python 범용)                          │
│  ├─ 스택트레이스 추출기                                    │
│  └─ 언어 감지기                                            │
│                                                            │
│  [Analysis Layer]                                          │
│  ├─ Simple Chain (기본) 또는 LangGraph Agent (필요시)      │
│  ├─ Tool: 파일 읽기                                        │
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

## 사전 정의: 테스트 케이스 10개

> MVP 성공 기준으로 사용. Week 8 완료 시 7개 이상 통과 필요.

| # | 언어 | 에러 타입 | 입력 (스택트레이스 요약) | 예상 출력 | 성공 기준 |
|---|------|----------|------------------------|----------|----------|
| 1 | Java | NullPointerException | `at com.example.UserService.getUser(UserService.java:42)` | UserService.java 42번 라인 주변 코드 + null 체크 제안 | 정확한 파일/라인 식별 |
| 2 | Java | SQLException | `Connection refused to host: localhost:3306` | DB 연결 설정 관련 코드 + 연결 문자열 확인 제안 | 관련 설정 파일 식별 |
| 3 | Java | OutOfMemoryError | `Java heap space at com.example.DataProcessor.process` | 메모리 사용 코드 + 힙 설정/스트리밍 처리 제안 | 메모리 관련 코드 식별 |
| 4 | Java | ClassNotFoundException | `com.mysql.jdbc.Driver` | 의존성 설정 파일 + 드라이버 추가 제안 | pom.xml/build.gradle 식별 |
| 5 | Java | ConcurrentModificationException | `at java.util.ArrayList$Itr.next` | 컬렉션 순회 코드 + 동기화/CopyOnWrite 제안 | 해당 반복문 코드 식별 |
| 6 | Python | KeyError | `KeyError: 'user_id' at app/services/user.py:28` | user.py 28번 라인 + dict.get() 사용 제안 | 정확한 파일/라인 식별 |
| 7 | Python | ImportError | `No module named 'pandas'` | requirements.txt + 패키지 설치 제안 | 의존성 파일 식별 |
| 8 | Python | ConnectionError | `ConnectionError: HTTPSConnectionPool host='api.example.com'` | API 호출 코드 + 재시도/타임아웃 제안 | 네트워크 관련 코드 식별 |
| 9 | Python | TypeError | `TypeError: unsupported operand type(s) for +: 'int' and 'str'` | 타입 불일치 코드 + 형변환 제안 | 해당 연산 코드 식별 |
| 10 | Python | RecursionError | `maximum recursion depth exceeded` | 재귀 함수 코드 + 반복문 변환/깊이 제한 제안 | 재귀 함수 식별 |

### 평가 루브릭

각 테스트 케이스 점수 (0-7점):

| 항목 | 점수 | 기준 |
|------|------|------|
| 파일 식별 | 0-2 | 0: 실패, 1: 관련 파일, 2: 정확한 파일 |
| 라인 식별 | 0-1 | 0: 실패, 1: ±5 라인 이내 |
| 원인 분석 | 0-2 | 0: 무관, 1: 관련, 2: 정확 |
| 해결책 품질 | 0-2 | 0: 무관, 1: 일반적, 2: 실행 가능 |

**통과 기준:** 테스트 케이스당 5점 이상

---

## 사전 정의: 에러-해결책 스키마

```json
{
  "id": "java-npe-001",
  "language": "java",
  "error_type": "NullPointerException",
  "severity": "high",
  "stack_trace_pattern": "at .*\\.(get|find|load).*\\(.*\\.java:\\d+\\)",
  "common_causes": [
    "null 체크 누락",
    "Optional 미사용",
    "초기화되지 않은 필드"
  ],
  "root_cause_template": "{class}의 {method}에서 null 값을 참조했습니다.",
  "solutions": [
    {
      "description": "null 체크 추가",
      "code_example": "if (obj != null) { ... }",
      "priority": 1
    },
    {
      "description": "Optional 사용",
      "code_example": "Optional.ofNullable(obj).map(...)",
      "priority": 2
    }
  ],
  "verification_steps": [
    "해당 메서드의 파라미터에 @Nullable 어노테이션 확인",
    "호출부에서 null 전달 여부 확인",
    "단위 테스트에 null 케이스 추가"
  ],
  "related_errors": ["IllegalArgumentException", "IllegalStateException"],
  "tags": ["null-safety", "defensive-programming"]
}
```

### 초기 데이터셋 목표

| 언어 | 목표 개수 | 우선순위 에러 타입 |
|------|----------|------------------|
| Java | 15개 | NPE, SQLException, OOME, IOException, ClassNotFound |
| Python | 10개 | KeyError, ImportError, TypeError, ConnectionError, ValueError |

---

## Phase 1: MVP (Week 1-10)

### Week 1: 환경 세팅 + 로그 파서 기초

**목표:** 개발 환경 구축, 로그 파싱 기초 구현

**학습 내용:**
- [ ] Python 프로젝트 구조 (Poetry 사용)
- [ ] 로그 포맷 이해 (Java, Python 스택트레이스)
- [ ] 정규식 기반 파싱

**구현 태스크:**

| 태스크 | 결과물 파일 | 완료 기준 |
|--------|------------|----------|
| 프로젝트 초기화 | `pyproject.toml` | Poetry install 성공 |
| Java 로그 파서 | `src/parsers/java.py` | JavaLogParser.parse() 구현 |
| Python 로그 파서 | `src/parsers/python.py` | PythonLogParser.parse() 구현 |
| 언어 자동 감지 | `src/parsers/detector.py` | detect_language() 정확도 90%+ |
| 단위 테스트 | `tests/test_parsers.py` | 10개 테스트 통과 |

**결과물:**
```bash
log-detective parse --file error.log
# Output: 파싱된 스택트레이스 JSON
```

**리소스 벤치마크:**
- [ ] 파싱 속도: 1000줄 < 1초
- [ ] 메모리 사용량: < 50MB

**주간 체크포인트:**
- 월요일: 환경 세팅 완료
- 수요일: Java 파서 완료
- 금요일: Python 파서 + 테스트 완료

---

### Week 2-3: Vector DB + 임베딩 (2주)

> ⚠️ **확장된 일정:** Vector DB 학습 곡선을 고려하여 2주로 확장

**목표:** Chroma 사용법 습득, 소스 코드 임베딩 전략 확립

**Week 2 학습 내용:**
- [ ] 임베딩 개념 (텍스트 → 벡터, 유사도 검색)
- [ ] Chroma 기본 사용법 (CRUD, 메타데이터)
- [ ] OpenAI 임베딩 API 연동

**Week 2 구현 태스크:**

| 태스크 | 결과물 파일 | 완료 기준 |
|--------|------------|----------|
| Chroma 설치/설정 | `src/indexer/chroma_client.py` | 기본 CRUD 동작 |
| 임베딩 생성기 | `src/indexer/embedder.py` | OpenAI API 연동 성공 |
| 간단한 검색 테스트 | `tests/test_embedder.py` | 유사 텍스트 검색 성공 |

**Week 3 학습 내용:**
- [ ] 청킹 전략 비교 (파일별 vs 함수별 vs 고정 크기)
- [ ] 청킹 품질 평가 방법
- [ ] Chroma persistent 모드

**Week 3 구현 태스크:**

| 태스크 | 결과물 파일 | 완료 기준 |
|--------|------------|----------|
| 코드 청킹 로직 | `src/indexer/chunker.py` | 파일별 청킹 (max 1000 토큰) |
| 소스 인덱싱 | `src/indexer/source_indexer.py` | 프로젝트 폴더 인덱싱 |
| 검색 테스트 | `tests/test_search.py` | 쿼리 → 관련 코드 검색 |

**결과물:**
```bash
log-detective index --repo /path/to/project
log-detective search --query "NullPointerException in UserService"
# Output: 관련 소스 코드 조각들 (상위 5개)
```

**청킹 전략 결정:**

| 전략 | 장점 | 단점 | 결정 |
|------|------|------|------|
| 파일별 | 구현 간단, 컨텍스트 유지 | 대용량 파일 문제 | **MVP 채택** |
| 함수별 | 정밀한 검색 | AST 파싱 필요, 복잡 | Phase 2 |
| 고정 크기 | 일관된 크기 | 컨텍스트 손실 | 미채택 |

**리소스 벤치마크:**
- [ ] 임베딩 생성: 파일 100개 < 5분
- [ ] Vector DB 메모리: < 500MB (1만 청크 기준)
- [ ] 검색 응답: < 500ms

---

### Week 4: GitHub 연동 + 소스 인덱싱

**목표:** GitHub 레포 클론, 자동 인덱싱 파이프라인

**학습 내용:**
- [ ] GitHub API 기초 (인증, 레포 정보)
- [ ] Git 명령어 프로그래매틱 실행 (GitPython)
- [ ] 증분 업데이트 전략

**구현 태스크:**

| 태스크 | 결과물 파일 | 완료 기준 |
|--------|------------|----------|
| GitHub 클론 | `src/indexer/github.py` | 레포 클론 성공 |
| 파일 필터링 | `src/indexer/file_filter.py` | .gitignore 존중 |
| 증분 업데이트 | `src/indexer/incremental.py` | 변경 파일만 재인덱싱 |
| 인덱싱 상태 관리 | `src/indexer/state.py` | 마지막 동기화 기록 |

**결과물:**
```bash
log-detective github sync --repo https://github.com/user/project
log-detective github status
# Output: 인덱싱 상태, 파일 수, 마지막 동기화 시간
```

**리소스 벤치마크:**
- [ ] 전체 인덱싱: 중간 규모 레포 (500 파일) < 10분
- [ ] 증분 업데이트: < 1분

---

### Week 5: RAG 파이프라인 + 버퍼

> ⚠️ **버퍼 포함:** Week 2-4 지연 대비 여유 시간 확보

**목표:** 에러 로그 → 관련 소스 검색 → 컨텍스트 구성

**학습 내용:**
- [ ] RAG 아키텍처 이해 (Retrieve → Augment → Generate)
- [ ] 검색 품질 향상 기법 (reranking)
- [ ] 컨텍스트 윈도우 최적화

**구현 태스크:**

| 태스크 | 결과물 파일 | 완료 기준 |
|--------|------------|----------|
| 쿼리 변환 | `src/rag/query_builder.py` | 스택트레이스 → 검색 쿼리 |
| 검색기 | `src/rag/retriever.py` | top-k 관련 코드 반환 |
| 컨텍스트 빌더 | `src/rag/context_builder.py` | LLM 프롬프트 구성 |
| 품질 평가 | `tests/test_rag_quality.py` | 테스트 케이스 5개 통과 |

**결과물:**
```bash
log-detective analyze --error "java.lang.NullPointerException at ..."
# Output: 관련 소스 코드 + 컨텍스트 (LLM 호출 전)
```

**버퍼 활용:**
- Week 2-4 지연 시: 밀린 작업 완료
- 순조로울 시: 검색 품질 개선 실험

---

### Week 6: 에러 히스토리 DB 구축

**목표:** 과거 에러 + 해결책 데이터베이스 구축

**학습 내용:**
- [ ] 에러 데이터 구조 설계
- [ ] 유사도 검색 튜닝 (임계값 설정)

**구현 태스크:**

| 태스크 | 결과물 파일 | 완료 기준 |
|--------|------------|----------|
| 스키마 구현 | `src/history/schema.py` | ErrorSolution 모델 |
| 초기 데이터 | `data/error_history/seed.json` | Java 15개 + Python 10개 |
| 히스토리 검색 | `src/history/searcher.py` | 유사 에러 검색 |
| CLI 명령어 | `src/cli.py` | history add/search 명령 |

**결과물:**
```bash
log-detective history search --error "Connection refused"
# Output: 유사 에러 사례 + 해결책

log-detective history add --error "<error>" --solution "<solution>"
# 새 에러-해결책 추가
```

**초기 데이터 작성 가이드:**
1. 본인 개발 경험에서 자주 겪은 에러 우선
2. Stack Overflow에서 검증된 답변 참고 (복사 X, 이해 후 작성)
3. 각 에러당 최소 2개 해결책 포함

---

### Week 7: 분석 Chain 구현 (Simple First)

> ⚠️ **전략 변경:** LangGraph 대신 Simple Chain 먼저 구현

**목표:** 기본 분석 워크플로우 구현 (Chain 방식)

**학습 내용:**
- [ ] LangChain 기본 (PromptTemplate, Chain)
- [ ] 프롬프트 엔지니어링 기초
- [ ] 출력 파싱 (Structured Output)

**구현 태스크:**

| 태스크 | 결과물 파일 | 완료 기준 |
|--------|------------|----------|
| 분석 프롬프트 | `src/analyzer/prompts.py` | v1 프롬프트 템플릿 |
| 분석 Chain | `src/analyzer/chain.py` | 기본 분석 동작 |
| 출력 파서 | `src/analyzer/output_parser.py` | 구조화된 결과 |
| 프롬프트 버전 관리 | `prompts/v1/analyze.txt` | 버전별 프롬프트 저장 |

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

**LangGraph 결정 포인트:**

| 조건 | Simple Chain 유지 | LangGraph 전환 |
|------|------------------|----------------|
| 분기 로직 필요 | X | O |
| 반복 Tool 호출 | X | O |
| 상태 기반 흐름 | X | O |

**Week 7 종료 시 결정:** 테스트 케이스 5개 이상 통과하면 Chain 유지, 미달 시 Week 8에서 LangGraph 검토

---

### Week 8: Agent 업그레이드 (조건부) + 프롬프트 튜닝

**목표:** 필요시 LangGraph 전환, 프롬프트 품질 개선

**시나리오 A: Chain 충분 (테스트 5개+ 통과)**
- 프롬프트 튜닝에 집중
- Tool 추가 (파일 읽기)
- 에러 핸들링 강화

**시나리오 B: Agent 필요 (테스트 5개 미만)**
- LangGraph 학습
- Agent 워크플로우 구현
- Tool 연동

**구현 태스크 (시나리오 A):**

| 태스크 | 결과물 파일 | 완료 기준 |
|--------|------------|----------|
| 프롬프트 v2 | `prompts/v2/analyze.txt` | 품질 개선 |
| 파일 읽기 Tool | `src/analyzer/tools/file_reader.py` | 추가 컨텍스트 제공 |
| 에러 핸들링 | `src/analyzer/error_handler.py` | API 실패 시 fallback |
| A/B 테스트 | `tests/test_prompt_versions.py` | v1 vs v2 비교 |

**구현 태스크 (시나리오 B):**

| 태스크 | 결과물 파일 | 완료 기준 |
|--------|------------|----------|
| LangGraph 상태 | `src/agent/state.py` | 상태 정의 |
| Agent 그래프 | `src/agent/graph.py` | 워크플로우 구현 |
| Tool 연동 | `src/agent/tools.py` | 3개 Tool 동작 |

---

### Week 9: 실시간 모니터링

**목표:** 파일 워칭 구현

**학습 내용:**
- [ ] watchdog 라이브러리
- [ ] 디바운싱, Rate limiting
- [ ] 비동기 처리 (asyncio 기초)

**구현 태스크:**

| 태스크 | 결과물 파일 | 완료 기준 |
|--------|------------|----------|
| 파일 워칭 | `src/monitor/watcher.py` | 파일 변경 감지 |
| 에러 감지 | `src/monitor/error_detector.py` | ERROR 패턴 추출 |
| 디바운싱 | `src/monitor/debouncer.py` | 중복 에러 방지 |
| Rate Limiter | `src/monitor/rate_limiter.py` | 분당 10건 제한 |

**결과물:**
```bash
log-detective watch --file /var/log/app.log
# 실시간 에러 감지 및 분석
```

**리소스 목표:**

| 지표 | 목표 |
|------|------|
| 대기 시 CPU | < 3% |
| 대기 시 메모리 | < 300MB |
| 에러 감지 지연 | < 2초 |

---

### Week 10: Slack 알림 + CLI 완성 + MVP 검증

**목표:** MVP 완성, 테스트 케이스 검증

**구현 태스크:**

| 태스크 | 결과물 파일 | 완료 기준 |
|--------|------------|----------|
| Slack Webhook | `src/notifier/slack.py` | 알림 전송 성공 |
| CLI 완성 | `src/cli.py` | 모든 명령어 동작 |
| 설정 파일 | `config.example.yaml` | 설정 템플릿 |
| README | `README.md` | 설치/사용법 문서 |

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

# 히스토리
log-detective history search --error "<query>"
log-detective history add --error "<error>" --solution "<solution>"
```

**MVP 검증 체크리스트:**

| 항목 | 기준 | 상태 |
|------|------|------|
| 테스트 케이스 통과 | 7/10 이상 | [ ] |
| 수동 분석 | 동작 | [ ] |
| 실시간 모니터링 | 동작 | [ ] |
| Slack 알림 | 동작 | [ ] |
| README | 완성 | [ ] |
| 데모 시나리오 | 준비 | [ ] |

---

## Phase 2: 고도화 (Week 11-14)

> ⚠️ **범위 축소:** 핵심 기능에 집중, 다언어 지원은 미래 작업으로 이동

### Week 11: 비용 최적화 + 리소스 튜닝

**목표:** 분석 비용 절감, 리소스 사용량 최적화

**구현 태스크:**
- [ ] 에러 복잡도 분류 (단순/복잡)
- [ ] 모델 라우팅 (단순 → GPT-4o-mini, 복잡 → GPT-4o)
- [ ] 응답 캐싱 (동일 에러 재분석 방지)
- [ ] 비용 추적 로깅

**비용 목표:**

| 에러 유형 | 목표 비용 |
|----------|----------|
| 단순 에러 | < $0.01 |
| 복잡 에러 | < $0.10 |
| 평균 | < $0.04 |

---

### Week 12: API 서버 + 웹 UI (선택)

**목표:** 데모용 웹 인터페이스 또는 API

**옵션 A: Streamlit UI (권장)**
- [ ] 로그 입력 폼
- [ ] 분석 결과 표시
- [ ] 히스토리 조회

**옵션 B: FastAPI 서버**
- [ ] REST API 엔드포인트
- [ ] Swagger 문서
- [ ] 웹훅 수신

---

### Week 13: GCP 배포

**목표:** 클라우드 배포

**구현 태스크:**
- [ ] Dockerfile 작성
- [ ] GCP Cloud Run 배포
- [ ] 환경 변수 설정
- [ ] 헬스체크 구현

---

### Week 14: 포트폴리오 정리

**목표:** 문서화, 데모 준비

**구현 태스크:**
- [ ] GitHub README 완성 (GIF 데모 포함)
- [ ] 기술 블로그 포스트 작성
- [ ] 면접 데모 시나리오 3개 준비
- [ ] 아키텍처 다이어그램 작성

---

## 리소스 관리 가이드

### 비용 예산 (14주)

| 항목 | 예상 비용 |
|------|----------|
| GCP 크레딧 | $300 (무료) |
| OpenAI API | ~$60 |
| Claude API | ~$40 |
| 총 예상 | ~$100 (크레딧 내) |

### API 실패 처리

| 상황 | 대응 |
|------|------|
| Rate Limit (429) | 지수 백오프 재시도 (최대 3회) |
| Timeout | 30초 제한, 실패 로깅 |
| Vector DB 불가 | 캐시된 결과 반환 또는 에러 메시지 |
| LLM API 실패 | fallback 모델 시도 |

---

## 위험 요소 및 대응

| 위험 | 확률 | 영향 | 대응 |
|------|------|------|------|
| RAG 검색 품질 낮음 | 중 | 높음 | 청킹 전략 실험, reranking 추가 |
| Chain vs Agent 결정 지연 | 중 | 중 | Week 7 종료 시 강제 결정 |
| 리소스 초과 | 낮음 | 중 | 주간 벤치마크, 조기 최적화 |
| 에러 데이터 품질 | 중 | 중 | 직접 큐레이션 우선, 점진적 축적 |
| GCP 크레딧 소진 | 낮음 | 높음 | 비용 알림 $200 설정 |

---

## 성공 기준

### MVP (Week 10)

| 기준 | 목표 | 측정 방법 |
|------|------|----------|
| 테스트 케이스 | 7/10 통과 | 평가 루브릭 점수 5점+ |
| 분석 동작 | 성공 | CLI 명령어 실행 |
| 모니터링 | 성공 | 5분간 에러 감지 테스트 |
| 알림 | 성공 | Slack 메시지 수신 확인 |
| 문서 | 완성 | README로 설치 가능 |

### 최종 (Week 14)

| 기준 | 목표 |
|------|------|
| 배포 | GCP Cloud Run 동작 |
| 비용 | 평균 $0.04/분석 이하 |
| 데모 | 3개 시나리오 준비 |
| 블로그 | 1개 포스트 게시 |

---

## 폴더 구조

```
log-detective/
├── .sisyphus/
│   ├── plans/
│   │   └── log-detective-roadmap.md
│   └── logs/                    # 주간 회고 로그
│       └── week-01.md
├── src/
│   ├── __init__.py
│   ├── cli.py                   # CLI 진입점
│   ├── config.py                # 설정 관리
│   ├── parsers/                 # 로그 파서
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── java.py
│   │   ├── python.py
│   │   └── detector.py
│   ├── indexer/                 # 소스 인덱싱
│   │   ├── __init__.py
│   │   ├── github.py
│   │   ├── embedder.py
│   │   ├── chunker.py
│   │   └── chroma_client.py
│   ├── rag/                     # RAG 파이프라인
│   │   ├── __init__.py
│   │   ├── retriever.py
│   │   ├── query_builder.py
│   │   └── context_builder.py
│   ├── analyzer/                # 분석 (Chain/Agent)
│   │   ├── __init__.py
│   │   ├── chain.py
│   │   ├── prompts.py
│   │   ├── output_parser.py
│   │   └── tools/
│   │       └── file_reader.py
│   ├── history/                 # 에러 히스토리
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   └── searcher.py
│   ├── monitor/                 # 실시간 모니터링
│   │   ├── __init__.py
│   │   ├── watcher.py
│   │   ├── error_detector.py
│   │   ├── debouncer.py
│   │   └── rate_limiter.py
│   └── notifier/                # 알림
│       ├── __init__.py
│       └── slack.py
├── prompts/                     # 프롬프트 버전 관리
│   └── v1/
│       └── analyze.txt
├── tests/
│   ├── test_parsers.py
│   ├── test_embedder.py
│   ├── test_search.py
│   ├── test_rag_quality.py
│   └── test_prompt_versions.py
├── data/
│   └── error_history/
│       └── seed.json
├── pyproject.toml
├── README.md
├── Dockerfile
└── config.example.yaml
```

---

## 주간 회고 템플릿

`.sisyphus/logs/week-XX.md` 형식:

```markdown
# Week X 회고

## 완료한 것
-

## 배운 것
-

## 막힌 것
-

## 다음 주 계획
-

## 리소스 사용
- API 비용: $X.XX
- 작업 시간: X시간
```

---

## 미래 작업 (Future Work)

> Phase 2 이후 또는 다음 프로젝트로 이동

- [ ] Node.js 로그 파서
- [ ] Go 로그 파서
- [ ] 커스텀 정규식 패턴 지원
- [ ] 파서 플러그인 아키텍처
- [ ] Git blame 연동
- [ ] 멀티 레포 지원

---

*Plan created by Prometheus*
*Revised based on Momus review: 2025-01-27*
*Changes: MVP 10주 확장, 테스트 케이스 사전 정의, 스키마 명시, LangGraph 결정 포인트 추가, Phase 2 범위 축소*
