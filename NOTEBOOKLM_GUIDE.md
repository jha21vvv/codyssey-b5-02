# 🎙️ [NOTEBOOKLM_GUIDE.md] Google NotebookLM Audio Overview 딥다이브 팟캐스트 기획 및 학습 자료 키트

---

## 📌 1. Google NotebookLM 소스 코드 업로드 안내 (Upload Source Guide)

> **안내**: Google NotebookLM은 파이썬 소스 코드(`.py`) 확장자 직접 업로드를 지원하지 않으므로, 테스트 코드가 아닌 **실제 프로젝트 구현 소스 코드 전 파일(8개)**을 주석과 함께 단일 텍스트 파일로 모아둔 **[`NOTEBOOKLM_FULL_SOURCE.txt`](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/NOTEBOOKLM_FULL_SOURCE.txt)**를 제공합니다.

### 🌟 소스 코드 업로드 방법
NotebookLM에서 새 노트북을 생성한 후 아래 텍스트 파일을 업로드(Add Source -> Upload File)하시면, 불필요한 프롬프트나 테스트 코드 없이 **실제 핵심 구현 코드 전체**를 NotebookLM에 전달할 수 있습니다:

- **소스 코드 통합 파일**: **[`NOTEBOOKLM_FULL_SOURCE.txt`](file:///c:/Users/안재현/Documents/24_code/2609_codyssey/codyssey-b5-02/NOTEBOOKLM_FULL_SOURCE.txt)**
  - 포함 파일: `main.py`, `minigit/__init__.py`, `minigit/models.py`, `minigit/sorting.py`, `minigit/indexing.py`, `minigit/graph.py`, `minigit/repository.py`, `minigit/cli.py` (전 라인 2단 주석 포함)

---

## 🎧 2. NotebookLM 팟캐스트 오디오 생성 프롬프트 (Audio Overview Prompt)

> 아래 프롬프트를 복사하여 NotebookLM의 'Customize Audio Overview' 또는 대화창에 입력하세요:

```text
You are two charismatic tech podcast hosts (one senior systems architect and one enthusiastic junior developer mentor).
Host an engaging, insightful, and deep-dive technical conversation in Korean about the "Mini Git Pure Python Core Engine" project.

Key topics and storytelling flow:
1. [Hook & Problem Statement]: Why do developers use Git blindly without knowing that every commit is a graph node and hash? How does building a mini Git from scratch unlock deep algorithmic insights?
2. [Technical Decisions]:
   - Why did we strictly ban Python's built-in sorted() and list.sort(), and manually implement a Stable Merge Sort with O(N log N) complexity?
   - Why is the commit graph fundamentally a DAG (Directed Acyclic Graph), and why does Kahn's algorithm guarantee that parents are displayed before children?
   - How does the Inverted Index eliminate O(N) full scans and achieve instant O(1) keyword and author search?
3. [Memorable Analogies]: Explain the concepts using everyday metaphors:
   - Topological Sort = "Cooking Recipe Steps" (you cannot add noodles before boiling water).
   - Inverted Index = "Book Index at the back of a textbook" (flipping straight to the page instead of reading all 500 pages).
   - BFS Shortest Path = "Subway transfer route finder with alphabetical tie-breaking".
   - Merge Sort = "Sorting exam papers by splitting and merging with two pointers".
4. [Key Takeaways for Junior Engineers]: Highlight single responsibility principle (SRP), stable sorting edge cases, and deterministic tie-breaking.
Maintain an energetic, educational, and fun podcast banter with natural audio flow!
```

---

## 📚 3. 팟캐스트 원천 자료 요약 텍스트 (Deep Dive Knowledge Base)

### 3.1 호스트 대화 유도용 배경 스토리
- **개발 배경**: 대부분의 개발자들은 매일 `git commit`, `git merge`, `git branch`를 습관적으로 입력하지만, 커밋이 내부적으로 어떤 자료구조로 연결되어 있는지 알지 못합니다.
- **해결한 고충**: 외부 라이브러리(NetworkX 등)나 내장 헬퍼 함수 뒤에 숨겨진 추상화를 걷어내고, 커밋을 불변 노드로 만들고 부모 해시 포인터로 연결함으로써 Git의 실체를 직접 체감할 수 있도록 하였습니다.


2. **내장 `sorted()` 전면 배제 및 순수 수제 안정 병합 정렬(Merge Sort) 구현**:
   - 파이썬 내장 API를 금지한 제약 조건을 돌파하기 위해, 분할 정복(Divide and Conquer) 방식의 병합 정렬을 직접 바닥부터 작성했습니다.
   - 평균 및 최악 $O(N \log N)$의 시간 복잡도를 보장하며, 동일한 타임스탬프를 가진 커밋들의 초기 생성 순서를 100% 보존하는 **안정 정렬(Stability)**을 달성했습니다.
3. **DAG 위상 정렬과 $O(1)$ 역색인(Inverted Index) 아키텍처**:
   - "부모가 자식보다 무조건 먼저 출력된다"는 조건을 만족하기 위해 간선의 방향을 `부모 -> 자식`으로 모델링하고 Kahn's 알고리즘을 적용했습니다.
   - 메시지 검색 시 전체 커밋을 순회하는 $O(N)$의 비효율을 제거하기 위해 커밋 생성 시 토큰을 정규화하여 역색인 딕셔너리에 등록, $O(1)$ 초고속 검색을 구현했습니다.

### 3.3 일상 비유 모음집 (Metaphor Bank)
- **위상 정렬 (Topological Sort)**: 라면 끓이기 레시피 (물 끓이기 -> 면 넣기 -> 계란 풀기). 부모 작업이 완료되어야 자식 작업이 시작될 수 있음.
- **역색인 (Inverted Index)**: 두꺼운 전공 서적 맨 뒷장의 색인(찾아보기). 1페이지부터 다 읽지 않고 색인에서 단어를 찾아 해당 페이지로 바로 이동.
- **무방향 BFS 최단 경로 (Shortest Path)**: 역방향 탑승이 가능한 지하철 최소 환승 노선 탐색. 거리가 같을 땐 역 이름 가나다순으로 선택.
- **병합 정렬 (Merge Sort)**: 시험지 두 묶음을 책상 위에 두고 맨 위 번호만 비교하며 합치는 안정적인 분할 정복 작업.

### 3.4 주니어 개발자가 반드시 깨달아야 할 청취 포인트 3가지
1. **단일 책임 원칙(SRP)에 따른 깔끔한 모듈 분리**: 데이터 모델(`models.py`), 정렬 엔진(`sorting.py`), 역색인(`indexing.py`), 그래프 탐색(`graph.py`), 비즈니스 흐름(`repository.py`), CLI 인터페이스(`cli.py`)가 각자의 역할에만 집중하도록 설계하는 방법.
2. **부동소수점 시간(Timestamp) 동률 발생 시 안정 정렬의 위력**: 초고속 실행 환경에서 동일한 타임스탬프가 찍힐 때, 불안정 정렬은 순서를 뒤죽박죽으로 만들지만 안정 병합 정렬은 원래의 커밋 생성 순서를 그대로 지켜낸다는 점.
3. **결정론적(Deterministic) 알고리즘 설계**: BFS 최단 경로 탐색 시 여러 경로가 존재할 때, 실행 환경이나 탐색 순서에 휘둘리지 않고 사전순 규칙을 통해 항상 동일한 결과를 내도록 만드는 소프트웨어의 엄밀함.
