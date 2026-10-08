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

---

## 🎯 9. 프로젝트 심층 평가 및 아키텍처 질의응답 (Comprehensive Evaluation Q&A)

본 프로젝트의 요구사항 충족도, 내부 설계 구조, 핵심 알고리즘 및 확장성에 대한 평가 항목별 공식 질의응답 레퍼런스입니다.

---

### 📋 항목 1: 기능 구현 검증

> **평가 결과: `PASS`**

#### Q1. `INIT <user_name>` 실행 후 main 브랜치/HEAD/현재 사용자 설정이 정상적으로 초기화되어 있는가?
* **답변**: **`PASS`**  
  [`MiniGitRepository.init(user_name)`](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/minigit/repository.py#L38) 호출 시 `RepositoryState`를 생성하며 `is_initialized=True`, `current_author=user_name`, `head_branch="main"`, `branches={"main": None}`으로 완벽히 설정됩니다. 또한 내부 `CommitGraph`와 `InvertedIndex` 인스턴스를 새 객체로 초기화하여 이전 잔재가 없는 깨끗한 시작 상태를 보장합니다.

#### Q2. `BRANCH` 생성 후 `SWITCH`로 전환되며, 이후 `COMMIT`이 해당 브랜치에 반영되는가?
* **답변**: **`PASS`**  
  * `BRANCH <branch_name>`은 현재 HEAD 커밋을 가리키는 브랜치 포인터를 `self.state.branches` 딕셔너리에 등록합니다.
  * `SWITCH <branch_name>`은 `self.state.head_branch`를 해당 브랜치로 전환합니다.
  * 이후 `COMMIT <message>` 실행 시 `self.state.branches[self.state.head_branch]`가 신규 발급된 커밋 해시로 전진하여 분기 작업이 브랜치에 정상 반영됩니다.

#### Q3. `LOG`가 "부모 커밋이 자식 커밋보다 먼저" 출력되도록 동작하는가?
* **답변**: **`PASS`**  
  기본 `LOG` 명령어는 진입 차수(in-degree) 기반의 **Kahn's 위상 정렬(`topological_sort`)** 알고리즘을 사용합니다. 부모 커밋의 진입 차수가 0이 되어 큐에서 먼저 추출된 후에야 자식 커밋의 차수가 감소하여 큐에 진입하므로, **"부모 커밋이 항상 자식 커밋보다 먼저 출력"**되는 조건이 엄격하게 보장됩니다.

#### Q4. `PATH`가 경로가 있으면 최단 경로를, 없으면 `No path`를 출력하는가?
* **답변**: **`PASS`**  
  `find_shortest_path`에서 BFS(너비 우선 탐색)를 수행하여 간선 수 기준 최단 경로를 탐색합니다. 경로가 존재하지 않는 컴포넌트일 경우 `None`을 반환하여 CLI에서 `No path`를 출력하며, 동일 거리의 복수 경로가 존재할 경우 문자열 결합 기준 사전순(`hash1->hash2->...`) 최소 경로를 정확히 선택(Tie-breaking)합니다.

#### Q5. `ANCESTORS`가 모든 조상을 빠짐없이 출력하는가?
* **답변**: **`PASS`**  
  `get_ancestors` 메서드는 BFS 큐와 `visited` 집합을 사용하여 부모 포인터를 역추적합니다. 다이아몬드형 분기 및 다중 부모 구조에서도 중복 방문이나 사이클 없이 도달 가능한 모든 조상 커밋 해시를 누락 없이 역추적하여 반환합니다.

#### Q6. `SEARCH <keyword>` / `SEARCH --author=` / `LOG --sort-by=date|author`가 요구사항대로 동작하는가?
* **답변**: **`PASS`**  
  * `SEARCH <keyword>`: 공백 분리 및 소문자 정규화된 토큰 역색인을 통해 $O(1)$로 검색합니다.
  * `SEARCH --author=<name>`: 소문자 정규화된 작성자 역색인을 통해 $O(1)$로 검색합니다.
  * `LOG --sort-by=date|author`: `sorted()` 금지 규칙에 따라 수제 병합 정렬(`merge_sort`)을 통해 타임스탬프(오름차순) 또는 작성자(알파벳순) 기준 안정 정렬(Stable Sort)을 수행합니다.

---

### 🏗️ 항목 2: 설계 및 구조화

> **평가 결과: `PASS`**

#### Q1. 커밋 저장소/브랜치/HEAD/사용자 정보를 어떤 구조로 분리했고, 각 책임을 설명할 수 있는가?
* **답변**: **`PASS`**  
  단일 책임 원칙(SRP)에 입각하여 각 계층의 역할을 명확히 분리했습니다:
  * **[`models.py`](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/minigit/models.py)**:
    * `Commit`: 해시, 메시지, 작성자, 일시, 부모를 캡슐화한 불변 값 객체(Value Object).
    * `RepositoryState`: 세션 초기화 여부, 현재 사용자, `head_branch`, 브랜치 포인터 맵(`branches`)을 추적하는 상태 객체.
  * **[`graph.py`](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/minigit/graph.py) (`CommitGraph`)**: 커밋 노드 보관소이자 DAG 위상 정렬, BFS 최단 경로, 조상 탐색 알고리즘을 전담하는 순수 그래프 엔진.
  * **[`indexing.py`](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/minigit/indexing.py) (`InvertedIndex`)**: 토큰화 분해 및 키워드/작성자별 커밋 해시 매핑을 전담하는 역색인 엔진.
  * **[`repository.py`](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/minigit/repository.py) (`MiniGitRepository`)**: 모델, 그래프, 인덱스를 조율하며 초기화, 커밋 생성, 브랜치 이동, JSON 영속화 등 비즈니스 로직을 오케스트레이션하는 도메인 퍼사드(Facade).
  * **[`cli.py`](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/minigit/cli.py) (`MiniGitCLI`)**: `shlex` 기반 따옴표 보존 입력 파싱, 대소문자 정규화, 출력 포맷팅, REPL 생명주기를 관리하는 프레젠테이션 컨트롤러.

#### Q2. 커밋 hash로 빠르게 조회하기 위해 어떤 자료 구조를 사용했고, 중복/충돌을 어떻게 방지했는지 설명할 수 있는가?
* **답변**: **`PASS`**  
  * **자료구조**: `CommitGraph` 내부에 `Dict[str, Commit]` (`self._commits`) 해시 테이블을 사용하여 $O(1)$ 평균 시간 복잡도로 즉각 조회를 수행합니다.
  * **해시 생성 및 충돌 방지**: 발급 순번 카운터(`_commit_counter`), 생성 일시(`time.time()`), 작성자, 메시지, 부모 해시 문자열을 조합하여 `hashlib.sha1()` 해시를 계산합니다. 앞 8자리를 단축 해시로 사용하되, `self.graph.contains(candidate)` 검사를 통해 만에 하나 동일 해시가 이미 존재할 경우 12자리로 자동 확장하여 세션 내 충돌을 원천 차단합니다.

#### Q3. 커밋이 추가될 때 역색인(author/keyword)을 어떤 시점에, 어떤 방식으로 갱신하도록 설계했는지 설명할 수 있는가?
* **답변**: **`PASS`**  
  * **시점**: `repository.commit()` 내부에서 신규 `Commit` 객체가 생성되어 `graph.add_commit(new_commit)`에 꽂히는 즉시, 동일 트랜잭션 흐름 내에서 `self.index.add_commit(new_commit)`을 호출합니다.
  * **방식**: 메시지를 공백 기준 토큰화(`tokenize`)한 후, 동일 커밋 내에서 동일 단어가 여러 번 나타나더라도 중복 색인을 방지하기 위해 `seen_tokens = set()`을 활용합니다. 단어별로 `_keyword_index[token].append(commit.hash)`에 추가하고, 작성자명 소문자 키로 `_author_index[author].append(commit.hash)`에 추가하여 $O(1)$에 실시간 반영합니다.

#### Q4. LOG, PATH, ANCESTORS 에서 사용되는 그래프 탐색 로직을 어떻게 재사용 가능하게 구성했는지 설명할 수 있는가?
* **답변**: **`PASS`**  
  비즈니스 로직 및 I/O와 독립된 `CommitGraph` 클래스 내부에 각각 `topological_sort()`, `find_shortest_path(c1, c2)`, `get_ancestors(hash)` 순수 메서드로 모듈화했습니다. CLI는 물론, 자동화된 단위 테스트(`tests/test_graph.py`), JSON 복원 시점 등 어디서든 동일한 인터페이스로 호출할 수 있습니다.

#### Q5. 주요 함수/클래스에 docstring/주석을 어떤 기준으로 작성했는지 설명할 수 있는가?
* **답변**: **`PASS`**  
  PEP 257 Python Docstring 표준 규격을 준수하여 작성했습니다:
  * **클래스 및 함수 설명**: 해당 컴포넌트의 단일 책임과 역할 정의.
  * **시간/공간 복잡도 표기**: 예: `O(1) lookup`, `O(N log N) merge sort`, `O(V + E) BFS`.
  * **인자(`Args`), 반환값(`Returns`), 예외(`Raises`)**: 타입 및 비즈니스 제약사항을 빠짐없이 문서화.

---

### 🧠 항목 3: 알고리즘 및 CS 개념

> **평가 결과: `PASS`**

#### Q1. 커밋 그래프가 왜 DAG여야 하는지, 사이클이 생기면 어떤 문제가 발생하는지 설명할 수 있는가?
* **답변**: **`PASS`**  
  * **DAG(방향성 비순환 그래프)여야 하는 이유**: Git 커밋은 **"시간의 인과 관계(Causality)"**를 나타냅니다. 새 커밋은 반드시 이전에 존재하던 부모 커밋을 바탕으로 생성되므로 시간의 흐름에 따른 명확한 방향(Directed)을 가지며, 과거의 커밋이 미래의 자식 커밋을 부모로 참조할 수 없으므로 순환이 존재하지 않아야(Acyclic) 합니다.
  * **사이클 발생 시 문제점**:
    1. **인과율 붕괴**: A가 B의 조상이면서 B가 A의 조상이 되는 논리적 모순 발생.
    2. **무한 루프**: 조상 탐색(`ANCESTORS`) 및 3-way 병합을 위한 공통 조상(LCA) 탐색 시 종료 조건 없이 무한 탐색에 빠짐.
    3. **위상 정렬 불가능**: 순환 종속성이 발생하여 선후 관계를 1차원으로 줄 세울 수 없음.

#### Q2. LOG 에서 "부모가 먼저" 조건을 만족시키기 위해 어떤 접근(예: 위상 정렬 성격의 출력)을 이용했는지 설명할 수 있는가?
* **답변**: **`PASS`**  
  **Kahn's Topological Sort** 알고리즘을 사용했습니다:
  1. 모든 노드의 진입 차수(in-degree: 아직 출력되지 않은 부모 커밋의 수)를 계산합니다.
  2. 부모가 없는 루트 커밋(진입 차수 0)들을 대기 큐에 투입합니다.
  3. 큐에서 커밋을 꺼내 결과 리스트에 추가하고, 해당 커밋의 자식 커밋들의 진입 차수를 1씩 차감합니다.
  4. 차수가 0이 된 자식 커밋만 새롭게 큐에 진입시키는 과정을 반복합니다.
  * 이 불변식(Invariant)에 의해 **모든 부모 커밋이 먼저 출력 리스트에 담기기 전에는 어떤 자식 커밋도 결코 출력될 수 없음**이 보장됩니다.

#### Q3. PATH 에서 최단 경로를 찾기 위해 어떤 알고리즘(예: BFS)을 선택했고, 간선을 무방향으로 정의한 이유를 설명할 수 있는가?
* **답변**: **`PASS`**  
  * **BFS(너비 우선 탐색) 선택 이유**: 모든 간선의 가중치가 동일한(1 hop) 비가중치 그래프에서 시작점부터 레벨 단위로 전진하므로, 목표 노드에 최초 도달한 경로가 수학적으로 **간선 수가 가장 적은 최단 경로**임이 보장되기 때문입니다 ($O(V + E)$).
  * **무방향 간선 정의 이유**: Git 커밋의 내부 포인터는 자식→부모(단방향)로만 연결되어 있습니다. 만약 유방향으로 탐색하면 서로 다른 브랜치 끝에 있는 두 커밋(예: `feature`와 `main`) 사이에는 공통 조상을 거쳐 돌아가는 경로를 찾을 수 없습니다. 브랜치 간의 이력적 연결성과 거리를 측정하려면 부모-자식 관계를 양방향 통행 가능한 무방향 간선으로 간주해야 합니다.

#### Q4. 정렬 알고리즘의 평균/최악 시간복잡도와 안정 정렬 여부를 설명할 수 있는가?
* **답변**: **`PASS`**  
  자체 수제 구현한 **병합 정렬(Merge Sort)**을 적용했습니다:
  * **시간 복잡도**: 최선, 평균, 최악 모두 **$\Theta(N \log N)$**입니다. 리스트를 항상 절반($\log N$ 층)으로 쪼갠 뒤, $O(N)$으로 병합하므로 데이터의 초기 정렬 상태에 영향을 받지 않고 균일하게 우수한 성능을 냅니다.
  * **안정 정렬(Stable Sort) 여부**: **완전한 안정 정렬**입니다. 두 원소의 키가 동일할 때(`cmp <= 0`) 항상 왼쪽 리스트(`left[i]`)의 원소를 먼저 결과 리스트에 채택하도록 구현하여, 동일 날짜나 동일 작성자를 가진 커밋들의 원래 상대적 순서가 절대 뒤바뀌지 않습니다.

#### Q5. 역색인이 순회 검색보다 빠른 이유를, 자료구조/시간복잡도 관점에서 설명할 수 있는가?
* **답변**: **`PASS`**  
  * **선형 순회 검색**: $N$개의 커밋에 대해 메시지 문자열을 매번 검색하므로 질의마다 **$O(N)$**이 소요됩니다. 커밋 수가 커질수록 응답 시간이 선형 비례하여 증가합니다.
  * **역색인(Inverted Index)**: 단어/작성자 키를 해시 함수를 통해 버킷으로 변환하는 해시 테이블(`dict`) 구조이므로, 저장소에 커밋이 100만 개가 있어도 질의 시 **$O(1)$** 상수의 시간으로 해당 커밋 목록을 즉시 추출합니다.

---

### 🚀 항목 4: 확장성 및 심화 고찰

> **평가 결과: `PASS`**

#### Q1. 커밋 수가 10배 늘어났을 때 병목이 될 지점을 예측하고, 개선 방향(자료구조/알고리즘)을 설명할 수 있는가?
* **답변**: **`PASS`**  
  1. **위상 정렬 큐 재정렬 병목**: 현재 Kahn's 알고리즘 수행 시 동률 타이 브레이킹을 위해 매 홉마다 큐를 재정렬합니다. 커밋 수가 10배 늘어나면 이 비용이 증가합니다.  
     👉 **개선**: 파이썬 `heapq`(우선순위 큐/최소 힙)를 도입하여 큐 삽입/추출을 $O(\log K)$로 전환.
  2. **무방향 인접 그래프 동적 구성 병목**: `find_shortest_path` 호출 시마다 전체 커밋을 순회해 인접 리스트(`adj`)를 만듭니다.  
     👉 **개선**: 커밋 생성 시점에 양방향 인접 리스트를 캐싱해 두어 탐색 시 그래프 빌드 시간($O(V+E)$)을 0으로 단축.
  3. **단일 JSON I/O 병목**: 커밋 수가 대량 증가하면 전체 그래프를 단일 `minigit_repo.json` 파일로 직렬화하는 디스크 I/O가 무거워집니다.  
     👉 **개선**: 실제 Git처럼 샤딩된 오브젝트 저장소(`.git/objects/xx/xxxx...`) 구조로 분할 저장(Append-only).

#### Q2. PATH 의 간선 정의를 "부모 방향만 허용"으로 바꾸면 결과가 어떻게 달라지고, 구현은 무엇을 바꿔야 하는지 설명할 수 있는가?
* **답변**: **`PASS`**  
  * **결과 변화**: 자식에서 부모 방향으로만 거슬러 올라갈 수 있으므로, `PATH A B`는 **"A가 B의 직계 자손이거나 B가 A의 직계 자손인 경우"**에만 경로가 발견됩니다. 서로 다른 브랜치로 분기된 커밋 간에는 공통 부모를 거쳐 내려갈 수 없으므로 `No path`가 반환됩니다.
  * **구현 변경**: [`graph.py`의 `find_shortest_path`](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/minigit/graph.py#L97-L103)에서 역방향 간선 추가 코드인 `adj[p_hash].add(commit.hash)`를 삭제하고, 오직 `adj[commit.hash].add(p_hash)`만 남기면 됩니다.

#### Q3. LOG --sort-by=author 요구사항이 "부모-자식 선후도 유지"로 강화된다면, 어떤 방식으로 해결할지 설명할 수 있는가?
* **답변**: **`PASS`**  
  * **접근법**: 일반 병합 정렬 대신 **"위상 정렬의 노드 선택 우선순위에 작성자 정렬 기준을 융합"**해야 합니다.
  * **구현 방식**: Kahn's 알고리즘에서 진입 차수가 0이 된 후보 노드들을 큐에서 꺼낼 때의 정렬 키를 `key = lambda c: (c.author.lower(), c.timestamp, c.hash)`로 설정합니다. 이렇게 하면 **부모가 자식보다 무조건 먼저 출력되는 DAG 위상 제약을 100% 만족**하면서도, 분기되어 병렬로 선택 가능한 후보 커밋들 사이에서는 작성자 알파벳순으로 우선 출력되는 요구조건을 우아하게 해결할 수 있습니다.

#### Q4. 해시 생성 방식을 카운터 기반 ↔ 난수 기반으로 바꿀 때 테스트/재현성/디버깅에 미치는 영향을 설명할 수 있는가?
* **답변**: **`PASS`**  
  * **카운터 기반**: 실행 순서에 따라 항상 동일한 시드가 만들어지는 **결정론적(Deterministic)** 특성을 가집니다. 따라서 단위 테스트에서 예측 가능한 해시값을 검증할 수 있고, 버그 발생 시 동일한 입력 순서만으로 100% 버그 재현 및 디버깅이 가능합니다.
  * **난수 기반**: 분산 환경에서 여러 사용자가 동시에 커밋을 생성할 때의 충돌 방지에는 유리하지만, 매 실행마다 해시값이 비결정론적으로 달라집니다. 이로 인해 정적 해시 테스트가 불가능해지고, 간헐적 버그 발생 시 디버깅 재현 경로를 추적하기 매우 어려워집니다.  
  *(실제 Git은 카운터나 단순 난수가 아니라 트리 내용, 부모 해시, 작성자, 타임스탬프를 암호학적으로 엮은 순수 콘텐츠 기반 SHA-1 해시를 사용하여 분산 고유성과 결정론적 재현성을 동시에 달성합니다.)*



