# 🚀 Mini Git: Pure Python CLI 분산 버전 관리 시스템

> 외부 패키지(`pip`) 및 내장 정렬 API(`sorted()`, `list.sort()`) 없이 순수 Python 3.10+ 표준 라이브러리만을 사용하여 구현한 **CLI 기반 Mini Git 코어 엔진**입니다.

---

## 📌 1. 프로젝트 소개 및 과제 목표

Git은 커밋 하나하나가 **방향성 비순환 그래프(DAG)**와 **해시(Hash)** 구조로 연결되어 동작합니다. 본 프로젝트는 Git의 내부 핵심 원리를 바닥부터 직접 구현하여 아래의 핵심 컴퓨터 과학 개념을 체득하는 것을 목표로 합니다:

1. **커밋 그래프 (DAG)**: 왜 Git 커밋 그래프는 순환이 없는 방향성 비순환 그래프인가?
2. **위상 정렬 (Topological Sort)**: "부모 커밋이 항상 자식 커밋보다 먼저 출력"되기 위한 Kahn's 알고리즘 적용.
3. **무방향 최단 경로 (BFS)**: 커밋 간의 최단 거리를 탐색하고 동률 발생 시 사전순(Lexicographical) 타이 브레이킹.
4. **역색인 (Inverted Index)**: $O(N)$ 전체 순회를 배제하고 $O(1)$ 즉시 검색을 지원하는 키워드 및 작성자 색인.
5. **순수 수제 안정 병합 정렬 (Merge Sort)**: Python 내장 정렬 API 전면 금지 제약 하에서 $O(N \log N)$ 안정 정렬 직접 구현.

---

## 📂 2. 프로젝트 디렉토리 구조

```text
codyssey-b5-02/
├── minigit/
│   ├── __init__.py           # 공개 패키지 인터페이스 및 심볼 노출
│   ├── models.py             # Commit (불변 노드) 및 RepositoryState 도메인 모델
│   ├── sorting.py            # sorted() 금지 대응 순수 수제 안정 병합 정렬 (Merge Sort)
│   ├── indexing.py           # InvertedIndex (O(1) 키워드 및 작성자 역색인 엔진)
│   ├── graph.py              # CommitGraph (위상 정렬, 무방향 BFS 최단 경로, 조상 탐색)
│   ├── repository.py         # MiniGitRepository (INIT, COMMIT, BRANCH 등 비즈니스 오케스트레이션)
│   └── cli.py                # MiniGitCLI (shlex 기반 REPL 파서 및 출력 포맷터)
├── tests/
│   ├── __init__.py
│   ├── test_sorting.py       # 병합 정렬 무결성, 안정성, 복합키 테스트
│   ├── test_indexing.py      # 역색인 토큰화, 중복 방어, O(1) 검색 테스트
│   ├── test_graph.py         # 위상 정렬, BFS 최단 경로, 조상 탐색 테스트
│   ├── test_repository.py    # 저장소 상태 전이, 커밋 발급, 정렬 연동 테스트
│   └── test_cli.py           # REPL 문법, 따옴표 인자, 한글 인코딩, 에러 핸들링 테스트
├── diagrams/                 # [Matplotlib 생성] 고해상도 아키텍처 다이어그램 PNG 4종
│   ├── architecture_1_dag_topological.png
│   ├── architecture_2_inverted_index.png
│   ├── architecture_3_bfs_shortest_path.png
│   └── architecture_4_merge_sort.png
├── scripts/
│   ├── generate_diagrams_matplotlib.py # Matplotlib 기반 4대 아키텍처 이미지 생성 스크립트
│   ├── build_notebooklm_source.py      # NotebookLM용 단일 텍스트 파일 빌더
│   └── draw_architectures.py           # 아키텍처 다이어그램 텍스트 출력 스크립트
├── main.py                   # CLI 진입 엔트리 포인트 (python main.py)
├── PLAN.md                   # [Step 1] 아키텍처 및 요구사항 분해 계획서
├── 스터디.md                  # [Step 4] 원본 전문, 1:1 대조 매핑표, 일상 비유, 다이어그램
├── REPORT.md                 # [Step 5] 세부 업무 리포트 (아키텍처, 벤치마크, 엣지케이스)
├── NOTEBOOKLM_GUIDE.md       # [Step 6] NotebookLM 오디오 팟캐스트 기획 및 학습 자료 키트
├── NOTEBOOKLM_FULL_SOURCE.txt# [NotebookLM 업로드용] 실제 핵심 소스 코드 8개 파일 모음 (테스트/프롬프트 제외)
└── README.md                 # 프로젝트 종합 가이드 (본 문서)
```

---

## ⚡ 3. 빠른 실행 가이드

### 3.1 실행 환경
- **Python**: 3.10 이상 권장 (3.10+)
- **외부 의존성**: 없음 (`pip install` 불필요, Zero-Dependency)

### 3.2 CLI 실행
```bash
python main.py
```

실행 후 `mini-git> ` 프롬프트가 나타납니다.
> 💾 **자동 파일 저장 & 복원 지원**: `main.py` 실행 시 모든 작업 내역(커밋, 브랜치, 상태)이 `minigit_repo.json`에 자동으로 실시간 저장되며, 프로그램을 종료했다가 다시 실행해도 이전 상태가 그대로 복원됩니다.

---

## 💻 4. CLI 명령어 레퍼런스

| 명령어 | 형식 | 설명 및 예시 |
| :--- | :--- | :--- |
| `INIT` | `INIT <user_name>` | 저장소 초기화, `main` 브랜치 및 `HEAD` 생성, 사용자 등록.<br>`mini-git> INIT "Alex Developer"` |
| `BRANCH` | `BRANCH <branch_name>` | 현재 HEAD 커밋을 가리키는 신규 브랜치 생성.<br>`mini-git> BRANCH feature-login` |
| `SWITCH` | `SWITCH <branch_name>` | HEAD를 지정한 브랜치로 전환.<br>`mini-git> SWITCH feature-login` |
| `COMMIT` | `COMMIT <message>` | 현재 HEAD를 부모로 하는 신규 커밋 생성 및 고유 해시 발급, 역색인 갱신.<br>`mini-git> COMMIT "feat: add oauth login"` |
| `LOG` | `LOG` | 부모 커밋이 항상 자식 커밋보다 먼저 출력되는 **위상 정렬(Topological Sort)** 로그 출력.<br>`mini-git> LOG` |
| `LOG` | `LOG --sort-by=date\|author` | 자체 수제 Merge Sort를 이용한 날짜(timestamp) 또는 작성자(author) 기준 정렬 출력.<br>`mini-git> LOG --sort-by=date` |
| `PATH` | `PATH <c1> <c2>` | 부모-자식 연결을 무방향 간선으로 간주한 **최단 경로(BFS)** 탐색 (없으면 `No path`, 동률 시 사전순 최소).<br>`mini-git> PATH 1a2b3c4d 5e6f7a8b` |
| `ANCESTORS` | `ANCESTORS <commit_hash>` | 해당 커밋으로부터 부모 포인터를 역추적하여 도달 가능한 모든 조상 커밋 출력.<br>`mini-git> ANCESTORS 5e6f7a8b` |
| `SEARCH` | `SEARCH <keyword>` | 역색인(Inverted Index) 기반 키워드 커밋 검색 ($O(1)$ 즉시 조회).<br>`mini-git> SEARCH login` |
| `SEARCH` | `SEARCH --author=<name>` | 역색인(Inverted Index) 기반 작성자별 커밋 검색.<br>`mini-git> SEARCH --author="Alex Developer"` |
| `EXIT/QUIT` | `exit` 또는 `quit` | REPL 인터페이스 안전 종료.<br>`mini-git> exit` |

---

## 🧪 5. 초고속 단위 테스트 실행

Zero-Cost 인메모리 Mock 테스트로 0.01초 이내에 28개 테스트를 100% 통과합니다:

```bash
python -m unittest discover -s tests -v
```

**실행 결과**:
```bash
Ran 28 tests in 0.004s
OK
```

---

## 🔍 6. 7단계 완료 산출물 인덱스

본 프로젝트는 `PROJECT_WORKFLOW_PROMPT_TEMPLATE.md`에 명시된 7단계 마스터 프로세스에 따라 완결되었습니다:

- **[Step 1. PLAN]**: [PLAN.md](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/PLAN.md) (요구사항 분해 및 시스템 아키텍처 계획서)
- **[Step 2. BUILD]**: `minigit/` 모듈 및 [main.py](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/main.py) (SRP 단일 책임 원칙 준수 순수 구현)
- **[Step 3. TEST AUTOMATION]**: `tests/` 단위 테스트 슈트 (28개 테스트 전원 통과, 0.004초)
- **[Step 4. AUDIT & STUDY DOC]**: [스터디.md](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/스터디.md) (과제 원문 전문, 1:1 대조표, 주니어 일상 비유, 4대 아키텍처 다이어그램)
- **[Step 5. REFINE]**: [REPORT.md](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/REPORT.md) (타임스탬프 동률 안정 정렬 보존, 한글 유니코드, 따옴표 파싱 엣지케이스 방어 리포트)
- **[Step 6. NOTEBOOKLM PROMPT]**: [NOTEBOOKLM_GUIDE.md](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/NOTEBOOKLM_GUIDE.md) (NotebookLM 팟캐스트 기획 프롬프트 및 원천 자료 키트)
- **[Step 7. 2-TIER COMMENTS]**: 전체 소스 코드 라인별 `[1차: 기술적/문법적 설명]` + `[2차: 주니어 눈높이 현실 비유]` 주석 100% 반영 완료

---

## 🎯 7. [평가자용] 기능 검증 및 라이브 시연 시나리오 (Demo Guide)

과제 요구사항에 명시된 **저장소 초기화, 브랜치 관리, 위상 정렬 로그, 수제 병합 정렬, 역색인 검색, 최단 경로 BFS, 조상 탐색, 예외 처리**의 전 과정을 실제 Git 소프트웨어 개발 작업 이력을 기록하며 직접 검증할 수 있는 시연 시나리오입니다.

### 7.1 실행 시작
터미널에서 프로그램 엔트리 포인트를 실행합니다:
```bash
python main.py
```
`mini-git>` 프롬프트가 나타나면 아래 명령어를 순서대로 입력합니다.

---

### 7.2 단계별 시연 스토리보드 (실제 개발 이력 기록)
> ⚠️ `python main.py`를 실행하면 자동으로 `mini-git>` 프롬프트가 뜹니다. 아래 명령어는 **`mini-git>`을 제외한 명령어 본문만 복사**하여 입력하세요.

#### 1단계: 저장소 초기화 및 기본 커밋 기록 (INIT & COMMIT)
```text
INIT "Alex Developer"
# ✅ 출력: Initialized empty Mini Git repository for Alex Developer. Switched to branch 'main'.

COMMIT "Initial commit: create README.md and license"
# ✅ 1번째 커밋 생성 (root 커밋, 해시 발급 예: [main a1b2c3d4])

COMMIT "feat: setup project architecture and core models"
# ✅ 2번째 커밋 생성 (main 브랜치에 직렬 연결)
```

#### 2단계: 기능 브랜치 생성 및 분기 작업 기록 (BRANCH & SWITCH)
```text
BRANCH feature-login
# ✅ 출력: Created branch 'feature-login' at <2번째_커밋_해시>

SWITCH feature-login
# ✅ 출력: Switched to branch 'feature-login'

COMMIT "feat: implement oauth login authentication"
# ✅ feature-login 브랜치에 3번째 커밋 생성

COMMIT "test: add unit tests for login module"
# ✅ feature-login 브랜치에 4번째 커밋 생성
```

#### 3단계: 메인 브랜치 복귀 및 병렬 작업 기록 (DAG 분기 형성)
```text
SWITCH main
# ✅ 출력: Switched to branch 'main'

COMMIT "docs: update API documentation and diagrams"
# ✅ main 브랜치에 5번째 커밋 생성 (feature-login과 공통 부모로부터 갈라져 나온 병렬 커밋)
```

#### 4단계: [과제 핵심 1] 부모가 먼저 출력되는 위상 정렬 로그 (LOG)
```text
LOG
```
* **검증 포인트**:
  * 최신순 나열이 아니라, **"부모 커밋이 항상 자식 커밋보다 먼저 출력"**(Kahn's Topological Sort)되는 것을 확인합니다.
  * 루트 커밋(`Initial commit`)이 가장 위에 출력되고, 그 자식들이 순서대로 출력됩니다.
  * 각 커밋마다 `commit <hash>`, `Author:`, `Date:`, `Parents:`, `메시지`가 완벽하게 식별됩니다.

#### 5단계: [과제 핵심 2] 순수 수제 Merge Sort 정렬 (LOG --sort-by)
> ⚠️ `sorted()`나 `list.sort()` 없이 자체 구현한 $O(N \log N)$ 병합 정렬로 정렬됩니다.
```text
LOG --sort-by=date
# ✅ 타임스탬프(오름차순) 기준 정렬 출력

LOG --sort-by=author
# ✅ 작성자 알파벳 순 기준 정렬 출력
```

#### 6단계: [과제 핵심 3] O(1) 역색인(Inverted Index) 검색 (SEARCH)
> ⚠️ 전체 커밋 순회($O(N)$) 없이 토큰화된 역색인 해시맵에서 $O(1)$로 즉시 조회합니다.
```text
# 1) 키워드 역색인 검색 (대소문자 무관 토큰 매칭)
SEARCH login
# ✅ 'feat: implement oauth login authentication', 'test: add unit tests for login module' 2개 커밋 즉시 반환

SEARCH documentation
# ✅ 'docs: update API documentation and diagrams' 커밋 즉시 반환

# 2) 작성자 역색인 검색
SEARCH --author="Alex Developer"
# ✅ Alex Developer가 작성한 모든 커밋 즉시 반환
```

#### 7단계: [과제 핵심 4] 무방향 최단 경로(BFS) 및 조상 탐색 (PATH & ANCESTORS)
> ⚠️ `LOG` 출력에서 확인한 실제 커밋 해시(앞 8자리)를 복사하여 아래 `<hash>` 자리에 넣어 실행합니다.
```text
# 1) 두 브랜치 끝 커밋 간의 무방향 최단 경로 (공통 부모를 거쳐 돌아가는 최소 간선 경로)
PATH <5번째_커밋_해시> <4번째_커밋_해시>
# ✅ 출력 예시: 5번째_해시 -> 2번째_해시(공통부모) -> 3번째_해시 -> 4번째_해시

# 2) 특정 커밋의 모든 조상 역추적 탐색
ANCESTORS <4번째_커밋_해시>
# ✅ 4번째 커밋의 부모(3번째), 조부모(2번째), 루트(1번째) 커밋이 빠짐없이 역추적되어 출력됨
```

#### 8단계: [과제 핵심 5] 예외 처리 및 표준 에러 메시지 검증
```text
SWITCH nonexistent
# ✅ 출력: Unknown branch: nonexistent

COMMIT
# ✅ 출력: Invalid args: COMMIT requires <message>

ANCESTORS 99999999
# ✅ 출력: Unknown commit: 99999999
```

#### 9단계: 종료
```text
quit
# ✅ 프로그램 안전 종료
```

---

### 7.3 평가자 10초 쾌속 복사/붙여넣기 테스트 팩
터미널에서 `python main.py` 실행 후, 아래 텍스트 블록 전체를 복사하여 터미널 창에 붙여넣기(Paste)하면 기본 시나리오가 자동으로 한 번에 수행됩니다:

```text
INIT "Evaluator"
COMMIT "Initial commit: create README.md and core system"
COMMIT "feat: implement DAG commit graph and models"
BRANCH feature-auth
SWITCH feature-auth
COMMIT "feat: implement oauth token authentication logic"
COMMIT "test: add comprehensive unit test for auth module"
SWITCH main
COMMIT "docs: write architecture documentation and user manual"
LOG
LOG --sort-by=date
SEARCH auth
SEARCH --author=Evaluator
SWITCH unknown-branch
```
*(위 일괄 입력 후 화면에 출력된 해시를 보고 `PATH <해시1> <해시2>` 또는 `ANCESTORS <해시>`를 입력하여 경로/조상 탐색을 즉시 검증할 수 있습니다.)*

---

## 📖 8. Mini Git CLI 전체 명령어 상세 가이드 (Complete Command Reference)

Mini Git CLI 환경(`mini-git> ` 프롬프트)에서 사용할 수 있는 모든 명령어의 **의미, 사용 방식, 실행 예시, 출력 결과, 주의사항**입니다.

### 📌 요약 치트시트

| 명령어 | 기본 문법 | 설명 |
| :--- | :--- | :--- |
| **`INIT`** | `INIT <user_name>` | 저장소 초기화, `main` 브랜치 생성 및 작성자 설정 |
| **`BRANCH`** | `BRANCH <branch_name>` | 현재 HEAD 커밋을 가리키는 신규 브랜치 생성 |
| **`SWITCH`** | `SWITCH <branch_name>` | HEAD를 지정한 브랜치로 전환 |
| **`COMMIT`** | `COMMIT <message>` | 현재 브랜치에 신규 커밋 생성 및 역색인 등록 |
| **`LOG`** | `LOG` | 부모가 먼저 출력되는 **위상 정렬(Topological Sort)** 로그 출력 |
| **`LOG` (옵션)** | `LOG --sort-by=date\|author` | 수제 병합 정렬 기반 타임스탬프 또는 작성자순 로그 출력 |
| **`PATH`** | `PATH <commit1> <commit2>` | 두 커밋 간의 무방향 **최단 경로(BFS)** 탐색 |
| **`ANCESTORS`** | `ANCESTORS <commit_hash>` | 특정 커밋의 모든 조상 커밋 역추적 탐색 |
| **`SEARCH`** | `SEARCH <keyword>` | $O(1)$ 역색인(Inverted Index) 기반 키워드 커밋 검색 |
| **`SEARCH` (옵션)**| `SEARCH --author=<name>` | $O(1)$ 역색인 기반 작성자별 커밋 검색 |
| **`EXIT` / `QUIT`** | `exit` 또는 `quit` | REPL 인터페이스 안전 종료 |

---

### 1. `INIT` - 저장소 초기화

* **의미**: Mini Git 저장소를 새롭게 초기화합니다. 작업자(`user_name`)를 등록하고, 기본 브랜치인 `main`을 생성하며 HEAD 포인터를 `main`으로 설정합니다. 기존에 등록된 커밋 그래프와 색인 노트를 깨끗하게 리셋합니다.
* **사용 방식**:
  ```text
  INIT <user_name>
  ```
  * 이름에 공백이 포함된 경우 큰따옴표(`"..."`)로 감싸야 합니다.
* **실행 예시**:
  ```text
  mini-git> INIT "Alex Developer"
  ```
* **출력 결과**:
  ```text
  Initialized empty Mini Git repository for Alex Developer. Switched to branch 'main'.
  ```
* **주의사항**:
  * `user_name`을 입력하지 않으면 `Invalid args: INIT requires <user_name>` 에러가 발생합니다.
  * 저장소를 초기화하기 전에는 다른 명령어(`COMMIT`, `BRANCH` 등)를 실행할 수 없습니다 (`Repository not initialized`).

---

### 2. `BRANCH` - 브랜치 생성

* **의미**: 현재 HEAD가 가리키고 있는 최신 커밋 위치에 새로운 브랜치 포인터를 생성합니다. (단, 현재 작업 브랜치가 바뀌지는 않습니다.)
* **사용 방식**:
  ```text
  BRANCH <branch_name>
  ```
* **실행 예시**:
  ```text
  mini-git> BRANCH feature-login
  ```
* **출력 결과**:
  ```text
  Created branch 'feature-login' at a1b2c3d4.
  ```
  *(커밋이 아직 없는 초기 상태에서 생성 시 `at (initial)`로 표시됩니다.)*
* **주의사항**:
  * 이미 존재하는 브랜치 이름을 입력하면 `Branch already exists: <branch_name>` 에러가 반환됩니다.
  * 브랜치 이름을 생략하면 `Invalid args: BRANCH requires <branch_name>` 에러가 반환됩니다.

---

### 3. `SWITCH` - 브랜치 전환

* **의미**: 작업 대상 활성 브랜치(HEAD)를 지정한 브랜치로 전환합니다. 이후 실행되는 `COMMIT`은 전환된 브랜치에 기록됩니다.
* **사용 방식**:
  ```text
  SWITCH <branch_name>
  ```
* **실행 예시**:
  ```text
  mini-git> SWITCH feature-login
  ```
* **출력 결과**:
  ```text
  Switched to branch 'feature-login'.
  ```
* **주의사항**:
  * 존재하지 않는 브랜치를 입력하면 `Unknown branch: <branch_name>` 에러가 반환됩니다.

---

### 4. `COMMIT` - 커밋 생성 및 저장

* **의미**: 현재 활성 브랜치의 최신 커밋을 부모(Parent)로 삼아 새로운 불변 커밋을 생성합니다. 고유한 SHA-1 단축 해시(8자리)를 발급하고, 커밋 메시지의 단어 토큰들과 작성자를 역색인(Inverted Index)에 자동 등록합니다.
* **사용 방식**:
  ```text
  COMMIT <message>
  ```
  * 메시지에 공백이 포함되므로 반드시 큰따옴표(`"..."`)로 감싸야 합니다.
* **실행 예시**:
  ```text
  mini-git> COMMIT "feat: add user authentication and jwt token"
  ```
* **출력 결과**:
  ```text
  [feature-login a1b2c3d4] feat: add user authentication and jwt token
  ```
* **주의사항**:
  * 커밋 메시지를 비우거나 따옴표를 닫지 않으면 `Invalid args: COMMIT requires <message>` 또는 `parsing quotes failed` 에러가 반환됩니다.
  * 저장소 내 동일 커밋에서 같은 단어가 여러 번 나와도 역색인에는 1회만 등록되어 중복을 방지합니다.

---

### 5. `LOG` - 커밋 히스토리 조회 (위상 정렬 및 수제 병합 정렬)

* **의미**: 저장소에 기록된 전체 커밋 목록을 상세 정보(해시, 작성자, 생성일시, 부모 커밋, 메시지)와 함께 출력합니다.
* **사용 방식**:
  1. **기본 실행 (위상 정렬, Topological Sort)**:
     ```text
     LOG
     ```
     * **핵심 동작**: Kahn's 알고리즘 기반 위상 정렬을 통해 **"부모 커밋이 항상 자식 커밋보다 먼저 출력"**됩니다.
  2. **정렬 옵션 지정 (수제 Merge Sort)**:
     ```text
     LOG --sort-by=date
     LOG --sort-by=author
     ```
     * `--sort-by=date`: 타임스탬프 기준 오름차순(오래된 순) 정렬.
     * `--sort-by=author`: 작성자 이름 기준 알파벳 오름차순 정렬.
* **출력 결과 예시**:
  ```text
  commit a1b2c3d4
  Author:    Alex Developer
  Date:      2026-10-06 14:00:00 (1791266400.00)
  Parents:   (root)
      Initial commit: setup repository

  commit 5e6f7a8b
  Author:    Alex Developer
  Date:      2026-10-06 14:05:00 (1791266700.00)
  Parents:   a1b2c3d4
      feat: add user authentication and jwt token
  ```
* **주의사항**:
  * 지원하지 않는 정렬 옵션을 입력할 경우 `Invalid args: --sort-by must be date or author` 에러가 반환됩니다.
  * 옵션을 2개 이상 입력하면 `Invalid args: LOG accepts at most one --sort-by option` 에러가 반환됩니다.

---

### 6. `PATH` - 두 커밋 간 무방향 최단 경로 탐색 (BFS)

* **의미**: 커밋 간의 부모-자식 관계를 무방향 간선으로 간주하여, 두 커밋 사이를 가장 적은 간선으로 이동할 수 있는 **최단 경로(Shortest Path)**를 BFS로 탐색합니다. (경로 길이가 같은 동률 경로가 존재할 경우 사전순 최소 경로를 선택합니다.)
* **사용 방식**:
  ```text
  PATH <commit1> <commit2>
  ```
* **실행 예시**:
  ```text
  mini-git> PATH a1b2c3d4 9c0d1e2f
  ```
* **출력 결과**:
  ```text
  a1b2c3d4 -> 5e6f7a8b -> 9c0d1e2f
  ```
  *(두 커밋 간 연결 경로가 없으면 `No path`가 출력됩니다.)*
* **주의사항**:
  * 존재하지 않는 커밋 해시를 입력하면 `Unknown commit: <commit_hash>` 에러가 반환됩니다.
  * 인자가 2개가 아니면 `Invalid args: PATH requires <commit1> <commit2>` 에러가 반환됩니다.

---

### 7. `ANCESTORS` - 모든 조상 커밋 역추적 탐색

* **의미**: 지정한 커밋으로부터 부모 포인터를 역방향으로 끝까지 추적하여, 해당 커밋의 계보에 존재하는 **모든 조상 커밋(부모, 조부모, 루트 커밋 등)**을 빠짐없이 수집하여 출력합니다.
* **사용 방식**:
  ```text
  ANCESTORS <commit_hash>
  ```
* **실행 예시**:
  ```text
  mini-git> ANCESTORS 9c0d1e2f
  ```
* **출력 결과**:
  ```text
  commit 5e6f7a8b
  Author:    Alex Developer
  Date:      2026-10-06 14:05:00 (1791266700.00)
  Parents:   a1b2c3d4
      feat: add user authentication and jwt token

  commit a1b2c3d4
  Author:    Alex Developer
  Date:      2026-10-06 14:00:00 (1791266400.00)
  Parents:   (root)
      Initial commit: setup repository
  ```
  *(루트 커밋처럼 조상이 없으면 `No ancestors.`가 출력됩니다.)*
* **주의사항**:
  * 존재하지 않는 커밋 해시를 입력하면 `Unknown commit: <commit_hash>` 에러가 반환됩니다.

---

### 8. `SEARCH` - 역색인(Inverted Index) 기반 초고속 검색

* **의미**: 전체 커밋을 일일이 전수 조사($O(N)$)하지 않고, 단어 또는 작성자별로 사전에 구축된 **역색인 해시 테이블에서 $O(1)$ 시간 복잡도로 즉시 커밋 목록을 조회**합니다.
* **사용 방식**:
  1. **키워드 검색 (기본)**:
     ```text
     SEARCH <keyword>
     ```
     * 대소문자를 구분하지 않으며, 공백 단위로 분리된 토큰과 매칭됩니다.
  2. **작성자 검색 (`--author=` 옵션)**:
     ```text
     SEARCH --author=<author_name>
     ```
     * 작성자 이름에 공백이 있을 경우 따옴표로 감쌉니다.
* **실행 예시**:
  ```text
  mini-git> SEARCH login
  mini-git> SEARCH --author="Alex Developer"
  ```
* **출력 결과**:
  * 조건에 매칭되는 커밋 카드들이 `format_commit` 양식으로 출력됩니다.
  * 매칭되는 커밋이 없으면 `No commits found.`가 출력됩니다.
* **주의사항**:
  * `--author=` 뒤에 이름을 지정하지 않으면 `Invalid args: --author requires a name` 에러가 반환됩니다.

---

### 9. `EXIT` / `QUIT` - REPL 세션 종료

* **의미**: Mini Git 대화형 REPL 인터페이스를 안전하게 종료하고 터미널 콘솔로 빠져나옵니다.
* **사용 방식**:
  ```text
  exit
  quit
  ```
  *(대소문자 무관, 또는 `Ctrl+C`, `Ctrl+D` 입력 시에도 안전하게 탈출합니다.)*
* **출력 결과**:
  ```text
  Exiting Mini Git.
  ```


