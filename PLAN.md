# 📋 [PLAN.md] Mini Git 프로젝트 아키텍처 및 구현 계획서

## 1. 프로젝트 개요 및 목표

- **프로젝트명**: Mini Git (CLI 기반 분산 버전 관리 시스템 코어 엔진)
- **목표**: 
  - Git의 내부 핵심 자료구조인 **DAG(방향성 비순환 그래프)**와 **해시(Hash)**, **역색인(Inverted Index)** 구조를 표준 라이브러리만을 사용하여 순수 파이썬으로 구현.
  - 외부 그래프 패키지(NetworkX 등) 및 파이썬 내장 정렬 API(`sorted()`, `list.sort()`) 사용을 철저히 배제하고, 직접 구현한 알고리즘(안정 병합 정렬, 위상 정렬, 너비 우선 탐색 BFS)으로 기능 완성.
  - REPL 인터페이스 환경에서 커밋 생성, 브랜치 이동, 최단 경로 추적, 역색인 검색 등을 직관적으로 수행하는 CLI 완성.

---

## 2. 요구사항 분해 및 제약 조건 분석

### 2.1 제약 조건
1. **런타임**: Python 3.10+
2. **라이브러리 제한**:
   - 그래프 전용 라이브러리 사용 일체 금지.
   - 정렬 관련 내장 함수 전면 금지 (`sorted()`, `list.sort()` 금지).
   - 순수 파이썬 기본 자료형(`list`, `dict`, `set`, `tuple`)과 기본 모듈(`hashlib`, `time`, `shlex`, `sys`, `unittest`)만 활용.
3. **영속성 및 범위**:
   - 파일 스냅샷 추적 및 네트워크 통신 제외.
   - 커밋 메타데이터 중심의 메모리 기반 세션 동작.

### 2.2 핵심 커맨드 규격
| 명령어 | 인자 형식 | 기능 설명 및 출력 규격 |
| :--- | :--- | :--- |
| `INIT` | `<user_name>` | 저장소 초기화, 기본 branch `main` 생성 및 `HEAD` 설정, `author` 등록 |
| `BRANCH` | `<branch_name>` | 현재 HEAD 커밋을 가리키는 새로운 브랜치 생성 |
| `SWITCH` | `<branch_name>` | HEAD를 지정한 브랜치로 전환 |
| `COMMIT` | `<message>` | 현재 HEAD를 부모로 하는 신규 커밋 생성 (단축/고유 Hash 발급), 역색인 갱신 |
| `LOG` | (없음) | 부모 커밋이 항상 자식 커밋보다 먼저 출력되는 **위상 정렬(Topological Sort)** 기반 전체 로그 출력 |
| `LOG` | `--sort-by=date\|author` | 자체 구현한 Merge Sort를 통해 날짜(timestamp) 또는 작성자(author) 기준으로 정렬 출력 |
| `PATH` | `<commit1> <commit2>` | 부모-자식 연결을 무방향 간선으로 간주한 **최단 경로(BFS)** 탐색. 없으면 `No path`. 동률 시 `hash1->hash2` 사전순 최소 경로 채택 |
| `ANCESTORS`| `<commit_hash>` | 해당 커밋으로부터 도달 가능한 모든 선조(조상) 커밋 목록 출력 |
| `SEARCH` | `<keyword>` | 역색인(Inverted Index) 기반 메시지 토큰 키워드 커밋 검색 |
| `SEARCH` | `--author=<name>` | 역색인(Inverted Index) 기반 작성자별 커밋 검색 |
| `EXIT/QUIT`| (없음) | REPL 루프 안전 종료 |

### 2.3 에러 처리 표준
- 잘못된 인자 수/형식: `Invalid args`
- 미초기화 상태에서 명령 실행: `Repository not initialized`
- 존재하지 않는 브랜치: `Unknown branch: <name>`
- 존재하지 않는 커밋 해시: `Unknown commit: <hash>`
- 이미 존재하는 브랜치 생성 시도: `Branch already exists: <name>`
- 빈 커밋 메시지: `Commit message cannot be empty`

---

## 3. 모듈별 아키텍처 및 책임 분리 (SRP)

```text
minigit/
├── __init__.py
├── models.py       # Commit, Branch, RepositoryData 등 도메인 엔티티 정의
├── sorting.py      # sorted(), list.sort()를 대체하는 순수 수제 안정 병합 정렬 (Merge Sort)
├── indexing.py     # InvertedIndex (키워드/작성자 O(1) 조회 색인 엔진)
├── graph.py        # CommitGraph (위상 정렬, 무방향 BFS 최단 경로, 조상 탐색)
├── repository.py   # MiniGitCore (INIT, BRANCH, SWITCH, COMMIT, SEARCH 조율 비즈니스 로직)
└── cli.py          # REPL 파서, shlex 따옴표 파싱, 입출력 포맷터
```

### 3.1 `minigit/models.py`
- `Commit` 데이터 클래스:
  - `hash`: 8자리 또는 40자리 고유 해시 문자열 (SHA-1 기반, 충돌 방지용 시퀀스/솔트 포함)
  - `message`: 커밋 메시지 본문
  - `author`: 커밋 작성자 이름
  - `timestamp`: 초 단위 부동소수점 타임스탬프 (생성 시점)
  - `parents`: 부모 커밋 해시 리스트 (`list[str]`)
- `RepositoryState`:
  - `current_author`: 현재 활성화된 작성자
  - `head_branch`: 현재 체크아웃된 브랜치 이름
  - `branches`: `{branch_name: commit_hash}` 딕셔너리
  - `is_initialized`: 초기화 여부 플래그

### 3.2 `minigit/sorting.py` (직접 구현 정렬 엔진)
- 알고리즘: **Merge Sort (병합 정렬)**
  - 평균 시간 복잡도: $O(N \log N)$
  - 최악 시간 복잡도: $O(N \log N)$
  - **안정 정렬(Stable Sort)** 특성 보장: 동일한 키 값을 가진 원소들의 입력 순서가 보존됨.
  - 내장 `sorted()`, `list.sort()` 일체 배제.
  - `merge_sort(iterable, key=lambda x: x, reverse=False)` 인터페이스 제공.

### 3.3 `minigit/indexing.py` (역색인 엔진)
- 키워드 추출: 커밋 메시지를 공백 기준 `split()`, 영문/문자열을 `lower()`로 정규화.
- 자료구조:
  - `keyword_index`: `dict[str, list[str]]` (토큰 -> 커밋 해시 리스트, 중복 방지 및 삽입 순서 보장)
  - `author_index`: `dict[str, list[str]]` (소문자/원문 매핑 -> 커밋 해시 리스트)
- 시간 복잡도: 검색 시 $O(1)$ 해시맵 룩업으로 후보 커밋 해시들을 즉각 반환. 전체 선형 탐색($O(N)$) 대비 압도적 고속화.

### 3.4 `minigit/graph.py` (커밋 그래프 알고리즘)
- **위상 정렬 (Topological Sort / Kahn's Algorithm)**:
  - 그래프 간선 방향: `부모 커밋 -> 자식 커밋`
  - 부모 커밋의 진입 차수(in-degree)는 0 (루트 커밋).
  - 진입 차수가 0인 노드부터 큐에 넣고 순차 탐색하여, **부모가 자식보다 무조건 먼저** 출력되는 순서열 산출.
  - 동률 진입 차수 처리 시 결정론적(deterministic) 순서 보장 (타임스탬프 또는 해시 순).
- **무방향 최단 경로 (Undirected Shortest Path BFS)**:
  - 부모-자식 간선을 양방향 간선으로 모델링.
  - BFS를 통해 최단 간선 수($k$) 경로 탐색.
  - 같은 최소 간선 수를 가진 경로가 여러 개일 경우, `hash1->hash2->...` 포맷으로 문자열 변환하여 **사전순(Lexicographical)으로 가장 작은 경로**를 정렬/선택.
- **모든 조상 탐색 (Ancestors Search)**:
  - 커밋에서 출발하여 `commit.parents` 방향(역방향 간선)으로만 BFS/DFS 탐색.
  - 사이클 방지 및 모든 도달 가능한 조상 노드 수집.

### 3.5 `minigit/repository.py` (리포지토리 엔진)
- 커밋 저장소: `dict[str, Commit]` (해시맵 기반 $O(1)$ 접근).
- 브랜치 관리 및 HEAD 포인터 갱신.
- `COMMIT` 호출 시 자동 해시 생성 및 역색인 업데이트.

### 3.6 `minigit/cli.py` & `main.py`
- 명령 파싱: `shlex.split`을 활용하여 큰따옴표/작은따옴표로 감싸진 공백 포함 인자(`"Add initial commit"`)를 정확히 파싱.
- 대소문자 무관 명령 처리(`init`, `INIT` 등).
- 옵션 파싱 (`--sort-by=date`, `--author=alice`).
- REPL 루프: `mini-git> ` 프롬프트, `exit`/`quit` 지원.

---

## 4. 7단계 워크플로우 진행 로드맵

1. **Step 1 (PLAN)**: 본 계획서 작성 및 구현 사양 확정 (`PLAN.md`).
2. **Step 2 (BUILD)**: `minigit` 핵심 패키지 및 모듈 점진적 구현, `main.py` 엔트리포인트 작성.
3. **Step 3 (TEST AUTOMATION)**: 초고속 Mock/단위 테스트(`tests/test_*.py`) 구현 및 통과율 100% 검증.
4. **Step 4 (AUDIT & STUDY DOC)**: 원본 과제 전문 100% 반영 및 1:1 대조 체크리스트, 주니어 눈높이 비유, 터미널 실행 예시, 아키텍처 다이어그램 4종이 포함된 `스터디.md` 작성.
5. **Step 5 (REFINE)**: 엣지 케이스 점검(공백, 한글, 특수문자, 대소문자, 미초기화 예외, 사전순 경로 타이브레이크 등) 및 세부 리포트(`REPORT.md`) 작성.
6. **Step 6 (NOTEBOOKLM PROMPT)**: Google NotebookLM Audio Overview 생성용 기획 프롬프트 및 원천 자료 문서(`NOTEBOOKLM_GUIDE.md`) 작성.
7. **Step 7 (2-TIER COMMENTS)**: 전체 소스 코드 라인별 [1차: 기술적/문법적 설명] + [2차: 주니어 눈높이 현실 비유] 주석 추가.
