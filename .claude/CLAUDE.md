# Log Detective - Project Context

## 프로젝트 개요

AI 기반 실시간 에러 로그 모니터링 및 분석 도구

| 항목 | 내용 |
|------|------|
| **목표** | 실시간 에러 로그 감지 + AI 원인 분석 Agent |
| **기간** | 14주 (10주 MVP + 4주 고도화) |
| **상태** | Week 1 진행 중 |

## 기술 스택

- Python 3.11+
- CLI: Click + Rich
- Vector DB: Chroma (Week 2-3)
- LLM: LangChain/LangGraph (Week 7-8)
- 배포: GCP Cloud Run

## 현재 진행 상황

### ✅ 완료
- 프로젝트 폴더 구조 생성
- pyproject.toml 작성
- 로그 파서 구현 (Java, Python)
- 언어 감지기 구현
- CLI 기본 구조 구현
- 테스트 코드 작성

### 🔄 진행 필요
- Poetry 설치 및 의존성 설치
- 테스트 실행 및 통과 확인
- Week 1 완료 후 커밋

## 핵심 명령어

```bash
# 의존성 설치
poetry install

# 테스트 실행
poetry run pytest

# CLI 실행
poetry run log-detective parse --file <log-file>
poetry run log-detective parse --text "<error-text>"

# 린트/포맷
poetry run black src tests
poetry run ruff check src tests
```

## 폴더 구조

```
log-detective/
├── src/
│   ├── cli.py              # CLI 진입점
│   ├── parsers/            # 로그 파서 (구현됨)
│   │   ├── base.py         # 기본 클래스
│   │   ├── java.py         # Java 파서
│   │   ├── python.py       # Python 파서
│   │   └── detector.py     # 언어 감지
│   ├── indexer/            # Week 2-3
│   ├── rag/                # Week 4-5
│   ├── analyzer/           # Week 6-8
│   ├── history/            # Week 6
│   ├── monitor/            # Week 9
│   └── notifier/           # Week 10
├── tests/
│   └── test_parsers.py     # 파서 테스트 (작성됨)
├── .sisyphus/plans/
│   └── log-detective-roadmap.md  # 14주 로드맵
└── pyproject.toml
```

## 로드맵 참조

상세 계획: `.sisyphus/plans/log-detective-roadmap.md`

### Week 1 태스크 (현재)

| 태스크 | 상태 |
|--------|------|
| 프로젝트 초기화 | ✅ 완료 |
| Java 로그 파서 | ✅ 완료 |
| Python 로그 파서 | ✅ 완료 |
| 언어 감지기 | ✅ 완료 |
| 단위 테스트 | ✅ 작성됨, 실행 필요 |
| CLI 기본 구조 | ✅ 완료 |

## 다음 단계

1. `poetry install`로 의존성 설치
2. `poetry run pytest`로 테스트 실행
3. 테스트 통과 확인 후 커밋
4. Week 1 완료 → Week 2 시작 (Vector DB + 임베딩)

## 테스트 케이스 (MVP 성공 기준)

로드맵에 10개 테스트 케이스 정의됨. Week 10 완료 시 7개 이상 통과 필요.

| # | 에러 타입 | 성공 기준 |
|---|----------|----------|
| 1 | Java NPE | 파일/라인 식별 |
| 2 | Java SQLException | 설정 파일 식별 |
| 3 | Java OOME | 메모리 코드 식별 |
| 4 | Java ClassNotFound | 의존성 파일 식별 |
| 5 | Java ConcurrentModification | 반복문 코드 식별 |
| 6 | Python KeyError | 파일/라인 식별 |
| 7 | Python ImportError | 의존성 파일 식별 |
| 8 | Python ConnectionError | 네트워크 코드 식별 |
| 9 | Python TypeError | 연산 코드 식별 |
| 10 | Python RecursionError | 재귀 함수 식별 |
