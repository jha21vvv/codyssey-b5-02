"""MiniGit repository management logic."""

# [1차]: JSON 직렬화 및 파일 입출력을 위해 json과 os 표준 모듈을 가져옵니다.
# [2차]: 작업실의 서류들을 영구 보관함에 넣고 꺼낼 수 있는 문서 보관 도구를 준비합니다.
import json
import os

# [1차]: SHA-1 해시값 계산을 위해 hashlib 표준 라이브러리를 가져옵니다.
# [2차]: 서류마다 위조 불가능한 고유 주민번호 도장을 파주기 위한 도장 기계를 준비합니다.
import hashlib

# [1차]: 현재 시각(Epoch time)을 초 단위 부동소수점으로 구하기 위해 time 모듈을 가져옵니다.
# [2차]: 커밋이 만들어진 순간을 정밀하게 기록하는 스톱워치를 준비합니다.
import time

# [1차]: 타입 안정성을 위한 표준 타이핑 심볼들을 가져옵니다.
# [2차]: 반환되는 데이터의 규격을 명확히 지정해 주는 이름표를 챙깁니다.
from typing import List, Optional, Tuple, Dict

# [1차]: 도메인 모델 클래스 Commit과 RepositoryState를 가져옵니다.
# [2차]: 커밋 문서 양식과 작업실 현황판을 가져옵니다.
from minigit.models import Commit, RepositoryState

# [1차]: 그래프 탐색 및 위상 정렬을 담당하는 CommitGraph 클래스를 가져옵니다.
# [2차]: 족보 관계와 길 찾기 지도를 담당하는 관리 본부를 가져옵니다.
from minigit.graph import CommitGraph

# [1차]: 키워드 및 작성자별 O(1) 조회를 제공하는 InvertedIndex 클래스를 가져옵니다.
# [2차]: 단어만 대면 즉시 페이지를 찾아주는 책 맨 뒤의 색인 카운터를 가져옵니다.
from minigit.indexing import InvertedIndex

# [1차]: 내장 정렬 API를 대신할 순수 수제 안정 병합 정렬 함수를 가져옵니다.
# [2차]: 파이썬 내장 정렬 없이도 안정적으로 카드를 줄 세워주는 자체 제작 정렬기를 가져옵니다.
from minigit.sorting import merge_sort


# [1차]: Mini Git의 전체 비즈니스 흐름을 조율하는 핵심 저장소 클래스입니다.
# [2차]: 작업실의 모든 도구(도화지, 서랍장, 색인 노트, 지도)를 총괄 관리하는 사령탑 매니저입니다.
class MiniGitRepository:
    """Core domain repository orchestrating models, indexing, sorting, and graph queries."""

    # [1차]: 저장소 객체 인스턴스를 초기화하는 생성자입니다 (선택적 JSON 파일 영속화 지원).
    # [2차]: 텅 빈 작업실 책상을 닦고 기본 도구들을 제자리에 배치합니다.
    def __init__(self, storage_path: Optional[str] = None) -> None:
        # [1차]: 세션 상태 객체를 기본값으로 생성합니다.
        # [2차]: 작업실 출입 기록판을 새로 겁니다.
        self.state = RepositoryState()
        # [1차]: 커밋 노드들을 관리할 CommitGraph 인스턴스를 생성합니다.
        # [2차]: 커밋 족보 지도판을 벽에 겁니다.
        self.graph = CommitGraph()
        # [1차]: 역색인을 관리할 InvertedIndex 인스턴스를 생성합니다.
        # [2차]: 검색용 색인 노트를 펼칩니다.
        self.index = InvertedIndex()
        # [1차]: 세션 내 커밋 생성 순번을 기록할 정수형 카운터입니다.
        # [2차]: 커밋이 몇 번째로 만들어졌는지 매기는 발급 번호표 기계입니다.
        self._commit_counter = 0
        # [1차]: 데이터 영속화를 위한 JSON 파일 경로를 설정합니다.
        # [2차]: 서류를 보관할 파일 보관함의 주소를 적어둡니다.
        self.storage_path = storage_path

        # [1차]: 영속화 경로가 주어지고 파일이 존재하면 기존 데이터를 복원합니다.
        # [2차]: 이전에 저장해둔 보관 파일이 있으면 책상 위에 그대로 펼쳐 놓습니다.
        if self.storage_path and os.path.exists(self.storage_path):
            self.load_from_json(self.storage_path)

    # [1차]: 저장소가 INIT으로 초기화되었는지 여부를 반환합니다.
    # [2차]: 작업실 전등이 켜져서 작업 가능한 상태인지 확인합니다.
    def is_initialized(self) -> bool:
        """Checks if repository has been initialized via INIT."""
        # [1차]: 상태 객체의 is_initialized 불리언 필드 값을 반환합니다.
        # [2차]: 전등 스위치가 ON인지 그대로 알려줍니다.
        return self.state.is_initialized

    # [1차]: 새로운 Mini Git 저장소를 초기화하고 기본 브랜치와 작성자를 설정합니다.
    # [2차]: 새로운 프로젝트 작업실을 정식 개관하고 메인 도화지와 작업자 이름을 정합니다.
    def init(self, user_name: str) -> str:
        """Initializes a new Mini Git repository."""
        # [1차]: 입력된 사용자명의 앞뒤 공백을 제거합니다.
        # [2차]: 작업자 명찰 양옆의 불필요한 빈칸을 깔끔하게 지웁니다.
        user_name = user_name.strip()
        # [1차]: 사용자명이 빈 문자열인 경우 유효성 검사 예외를 발생시킵니다.
        # [2차]: 명찰에 아무 글자도 안 적혀있으면 퇴짜를 놓습니다.
        if not user_name:
            raise ValueError("Invalid args: user_name cannot be empty")

        # [1차]: 상태 객체를 초기화하여 'main' 브랜치와 작성자를 등록합니다.
        # [2차]: 메인 도화지(main)를 펼치고 작업실 전등을 켭니다.
        self.state = RepositoryState(
            is_initialized=True,
            current_author=user_name,
            head_branch="main",
            branches={"main": None}
        )
        # [1차]: 그래프 저장소를 새로 생성하여 초기화합니다.
        # [2차]: 벽에 걸린 족보 지도를 깨끗한 새 지도판으로 교체합니다.
        self.graph = CommitGraph()
        # [1차]: 색인 엔진을 새로 생성하여 초기화합니다.
        # [2차]: 색인 노트를 새 노트로 바꿉니다.
        self.index = InvertedIndex()
        # [1차]: 커밋 발급 카운터를 0으로 리셋합니다.
        # [2차]: 번호표 발급기를 0번으로 초기화합니다.
        self._commit_counter = 0

        # [1차]: 자동 저장 로직을 호출합니다.
        # [2차]: 새로 열린 작업실 정보를 영구 보관함에 즉시 백업합니다.
        self._auto_save()

        # [1차]: 초기화 완료 메시지 포맷팅 문자열을 반환합니다.
        # [2차]: "작업실이 준비되었습니다!"라고 알리는 안내 방송입니다.
        return f"Initialized empty Mini Git repository for {user_name}. Switched to branch 'main'."

    # [1차]: 현재 HEAD 커밋을 가리키는 새로운 브랜치를 생성합니다.
    # [2차]: 현재 작업 중인 상태 그대로 새로운 작업 도화지를 한 장 더 복사해 만듭니다.
    def branch(self, branch_name: str) -> str:
        """Creates a new branch pointing to current HEAD commit."""
        # [1차]: 저장소 초기화 여부를 검사하고 미초기화 시 런타임 에러를 던집니다.
        # [2차]: 작업실 문도 안 열었는데 도화지를 달라고 하면 거절합니다.
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        # [1차]: 브랜치 이름의 공백을 제거합니다.
        # [2차]: 도화지 이름표의 빈칸을 다듬습니다.
        branch_name = branch_name.strip()
        # [1차]: 브랜치 이름이 비어있으면 예외를 발생시킵니다.
        # [2차]: 이름 없는 도화지는 만들 수 없다고 거절합니다.
        if not branch_name:
            raise ValueError("Invalid args: branch_name cannot be empty")

        # [1차]: 이미 동일한 이름의 브랜치가 존재하는지 검사합니다.
        # [2차]: 이미 같은 이름의 도화지가 책상에 놓여있는지 확인합니다.
        if branch_name in self.state.branches:
            raise ValueError(f"Branch already exists: {branch_name}")

        # [1차]: 현재 HEAD 브랜치가 가리키고 있는 커밋 해시를 가져옵니다.
        # [2차]: 지금 작업 중인 도화지가 몇 번째 그림을 가리키는지 확인합니다.
        current_head_commit = self._get_head_commit_hash()
        # [1차]: 새 브랜치를 딕셔너리에 추가하고 현재 커밋 해시를 가리키도록 설정합니다.
        # [2차]: 새 도화지 책갈피를 꽂고 그 자리를 그대로 북마크합니다.
        self.state.branches[branch_name] = current_head_commit
        # [1차]: 자동 저장 로직을 호출합니다.
        # [2차]: 새 도화지 정보를 영구 보관함에 즉시 백업합니다.
        self._auto_save()
        # [1차]: 브랜치 생성 성공 결과를 포맷팅하여 반환합니다.
        # [2차]: 새 도화지가 완성되었음을 안내합니다.
        return f"Created branch '{branch_name}' at {current_head_commit or '(initial)'}."

    # [1차]: HEAD가 가리키는 현재 활성 브랜치를 변경합니다.
    # [2차]: 지금 그리고 있는 도화지를 내려놓고 다른 도화지로 작업 도화지를 바꿉니다.
    def switch(self, branch_name: str) -> str:
        """Switches HEAD to the specified branch."""
        # [1차]: 저장소 초기화 여부를 검사합니다.
        # [2차]: 작업실이 오픈되었는지 점검합니다.
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        # [1차]: 대상 브랜치명의 앞뒤 공백을 제거합니다.
        # [2차]: 도화지 이름표를 깨끗이 닦습니다.
        branch_name = branch_name.strip()
        # [1차]: 브랜치명이 비어있을 경우 예외를 발생시킵니다.
        # [2차]: 빈 이름을 가진 도화지는 찾을 수 없음을 알립니다.
        if not branch_name:
            raise ValueError("Invalid args: branch_name cannot be empty")

        # [1차]: 대상 브랜치가 저장소에 존재하는지 딕셔너리에서 확인합니다.
        # [2차]: 그 이름의 도화지가 책상 위에 실제로 있는지 확인합니다.
        if branch_name in self.state.branches:
            # [1차]: HEAD 브랜치 포인터를 대상 브랜치로 변경합니다.
            # [2차]: 현재 작업 도화지 명찰을 그 도화지로 바꿉니다.
            self.state.head_branch = branch_name
            # [1차]: 자동 저장 로직을 호출합니다.
            # [2차]: 변경된 활성 도화지 정보를 영구 보관함에 즉시 백업합니다.
            self._auto_save()
            # [1차]: 브랜치 전환 성공 메시지를 반환합니다.
            # [2차]: "도화지를 교체했습니다"라고 알립니다.
            return f"Switched to branch '{branch_name}'."

        # [1차]: 존재하지 않는 브랜치일 경우 KeyError를 던집니다.
        # [2차]: 그런 도화지는 없다고 알립니다.
        raise KeyError(f"Unknown branch: {branch_name}")

    # [1차]: 중복 충돌이 발생하지 않는 유일한 단축 해시를 SHA-1 기반으로 생성합니다.
    # [2차]: 시계 시간, 순번, 내용물을 맷돌에 넣고 갈아서 세상에 하나뿐인 도장 번호를 만듭니다.
    def _generate_unique_hash(self, message: str, author: str, ts: float, parents: List[str]) -> str:
        """Generates a collision-resistant short hash for a new commit."""
        # [1차]: 커밋 생성 카운터를 1 증가시킵니다.
        # [2차]: 번호표 발급기 숫자를 1 올립니다.
        self._commit_counter += 1
        # [1차]: 해시 시드 문자열을 포맷팅합니다.
        # [2차]: 도장에 새겨넣을 재료(번호, 시간, 사람, 메시지, 부모)를 한 줄로 합칩니다.
        raw_seed = f"{self._commit_counter}:{ts}:{author}:{message}:{','.join(parents)}"
        # [1차]: UTF-8 바이트로 인코딩한 후 SHA-1 16진수 문자열을 계산합니다.
        # [2차]: 해시 맷돌을 돌려 40자리 16진수 비밀 번호를 뽑아냅니다.
        full_hash = hashlib.sha1(raw_seed.encode("utf-8")).hexdigest()
        # [1차]: 앞 8자리를 단축 해시 후보로 슬라이싱합니다.
        # [2차]: 앞 8글자만 잘라내어 읽기 편한 단축 명찰을 만듭니다.
        candidate = full_hash[:8]
        # [1차]: 그래프에 이미 동일한 단축 해시가 존재하는지 충돌 여부를 검사합니다.
        # [2차]: 혹시라도 똑같은 번호가 이미 있는지 확인합니다.
        if self.graph.contains(candidate):
            # [1차]: 충돌 시 12자리로 확장하여 유일성을 보장합니다.
            # [2차]: 겹친다면 더 길게 12글자를 사용하여 고유성을 지킵니다.
            candidate = full_hash[:12]
        # [1차]: 확정된 고유 해시 문자열을 반환합니다.
        # [2차]: 완성된 고유 커밋 지문 번호를 건네줍니다.
        return candidate

    # [1차]: 현재 HEAD를 부모로 하는 신규 커밋을 생성하고 인덱스와 브랜치를 갱신합니다.
    # [2차]: 지금까지 작업한 내용을 새 페이지로 묶고 책갈피를 한 장 앞으로 넘깁니다.
    def commit(self, message: str) -> Tuple[Commit, str]:
        """Creates a new commit on current HEAD branch and updates indexes."""
        # [1차]: 저장소 초기화 여부를 검사합니다.
        # [2차]: 작업실 문이 열려있는지 확인합니다.
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        # [1차]: 커밋 메시지의 앞뒤 공백을 제거합니다.
        # [2차]: 작업 설명 메모의 양옆 빈칸을 지웁니다.
        message = message.strip()
        # [1차]: 빈 메시지일 경우 예외를 발생시킵니다.
        # [2차]: 무슨 작업을 했는지 설명이 없으면 기록을 거절합니다.
        if not message:
            raise ValueError("Invalid args: commit message cannot be empty")

        # [1차]: 현재 등록된 작성자를 가져오며 미등록 시 "Unknown"을 사용합니다.
        # [2차]: 지금 도장을 찍을 작업자 이름을 확인합니다.
        author = self.state.current_author or "Unknown"
        # [1차]: 현재 에포크 타임스탬프를 초 단위 부동소수점으로 구합니다.
        # [2차]: 시계를 보고 지금 시각을 기록합니다.
        ts = time.time()

        # [1차]: 현재 활성 브랜치의 최신 커밋 해시를 부모 커밋으로 가져옵니다.
        # [2차]: 바로 직전 그림이 몇 번이었는지 부모 번호를 알아옵니다.
        parent_hash = self._get_head_commit_hash()
        # [1차]: 부모가 존재하면 리스트로 래핑하고, 첫 커밋이면 빈 리스트로 둡니다.
        # [2차]: 부모가 있으면 부모 명단에 넣고, 최초 커밋이면 시조(Root)가 됩니다.
        parents = [parent_hash] if parent_hash else []

        # [1차]: 고유한 커밋 해시 문자열을 생성합니다.
        # [2차]: 이번 새 작업물의 고유 지문 도장 번호를 발급받습니다.
        commit_hash = self._generate_unique_hash(message, author, ts, parents)
        # [1차]: 새로운 불변 Commit 객체를 생성합니다.
        # [2차]: 정식 커밋 문서 한 장을 완벽하게 작성합니다.
        new_commit = Commit(
            hash=commit_hash,
            message=message,
            author=author,
            timestamp=ts,
            parents=parents
        )

        # [1차]: 그래프 저장소에 커밋을 추가합니다.
        # [2차]: 족보 지도판에 새 커밋을 핀으로 꽂습니다.
        self.graph.add_commit(new_commit)

        # [1차]: 역색인 엔진에 커밋을 등록하여 키워드와 작성자를 인덱싱합니다.
        # [2차]: 색인 노트에 단어들과 작성자 이름을 즉시 적어 넣습니다.
        self.index.add_commit(new_commit)

        # [1차]: 현재 HEAD 브랜치의 최신 커밋 포인터를 새 커밋으로 전진시킵니다.
        # [2차]: 현재 도화지의 책갈피를 방금 그린 새 페이지로 옮깁니다.
        if self.state.head_branch is not None:
            self.state.branches[self.state.head_branch] = commit_hash

        # [1차]: 자동 저장 로직을 호출합니다.
        # [2차]: 새로운 커밋 서류와 브랜치 이동 결과를 영구 보관함에 즉시 백업합니다.
        self._auto_save()

        # [1차]: 콘솔에 출력할 포맷팅된 커밋 생성 결과 문자열을 조립합니다.
        # [2차]: "[main 1a2b3c4d] 로그인 기능 추가" 형태의 알림 문구를 만듭니다.
        msg = f"[{self.state.head_branch} {commit_hash}] {message}"
        # [1차]: 생성된 Commit 객체와 알림 문자열 튜플을 반환합니다.
        # [2차]: 결과 서류와 안내 문구를 함께 건넵니다.
        return new_commit, msg

    # [1차]: 현재 HEAD 브랜치가 참조하고 있는 최신 커밋 해시를 반환합니다.
    # [2차]: 지금 펼쳐놓은 도화지의 가장 최근 그림 번호를 읽어옵니다.
    def _get_head_commit_hash(self) -> Optional[str]:
        """Returns the commit hash currently referenced by HEAD branch."""
        # [1차]: 활성 브랜치가 없으면 None을 반환합니다.
        # [2차]: 도화지가 지정되어 있지 않으면 빈손을 반환합니다.
        if not self.state.head_branch:
            return None
        # [1차]: 브랜치 매핑 딕셔너리에서 현재 브랜치의 커밋 해시를 반환합니다.
        # [2차]: 도화지 책갈피에 적힌 번호를 돌려줍니다.
        return self.state.branches.get(self.state.head_branch)

    # [1차]: LOG 요구사항에 따라 커밋들을 정렬하여 반환합니다.
    # [2차]: 지금까지의 작업 이력들을 요청한 기준(족보순, 날짜순, 사람순)대로 줄 세워 보여줍니다.
    def log(self, sort_by: Optional[str] = None) -> List[Commit]:
        """Returns commits according to LOG specification."""
        # [1차]: 저장소 초기화 여부를 검사합니다.
        # [2차]: 작업실이 오픈되어 있는지 점검합니다.
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        # [1차]: sort_by 옵션이 없으면 부모가 먼저 출력되는 위상 정렬 결과를 반환합니다.
        # [2차]: 별도 정렬 명령이 없으면 부모님이 자식보다 먼저 나오는 정석 족보순으로 보여줍니다.
        if sort_by is None:
            return self.graph.topological_sort()

        # [1차]: 전체 커밋 객체 리스트를 복사해 가져옵니다.
        # [2차]: 저장소의 모든 커밋 카드들을 책상 위에 모읍니다.
        all_c = self.graph.all_commits()

        # [1차]: 날짜(timestamp) 기준 정렬 분기문입니다.
        # [2차]: 시간 순서대로 줄을 세우는 분기입니다.
        if sort_by == "date":
            # [1차]: 수제 병합 정렬을 통해 타임스탬프 기준으로 안정 정렬을 수행합니다.
            # [2차]: 스톱워치 시간 순서대로 정렬하되, 시간이 같으면 원래 만들어진 순서를 100% 지킵니다.
            return merge_sort(all_c, key=lambda c: c.timestamp)
        # [1차]: 작성자(author) 이름 기준 알파벳 정렬 분기문입니다.
        # [2차]: 작성자 이름의 가나다순/알파벳순으로 줄을 세우는 분기입니다.
        elif sort_by == "author":
            # [1차]: 수제 병합 정렬을 통해 소문자 작성자명 기준으로 안정 정렬을 수행합니다.
            # [2차]: 작성자 이름 명찰 순서대로 가지런히 줄을 세웁니다.
            return merge_sort(all_c, key=lambda c: c.author.lower())
        # [1차]: 유효하지 않은 정렬 옵션에 대해 예외를 발생시킵니다.
        # [2차]: 지원하지 않는 이상한 정렬 기준을 요구하면 거절합니다.
        else:
            raise ValueError(f"Invalid args: unknown sort option '{sort_by}'")

    # [1차]: 두 커밋 해시 사이의 무방향 최단 경로를 계산하여 해시 리스트를 반환합니다.
    # [2차]: 두 커밋 사이를 가장 적은 정거장을 거쳐 이동할 수 있는 최단 지하철 환승 노선을 찾습니다.
    def path(self, commit1: str, commit2: str) -> Optional[List[str]]:
        """Calculates undirected shortest path between commit1 and commit2."""
        # [1차]: 저장소 초기화 여부를 검사합니다.
        # [2차]: 작업실이 열려있는지 확인합니다.
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        # [1차]: 인자 문자열의 앞뒤 공백을 제거합니다.
        # [2차]: 출발지와 목적지 번호표의 빈칸을 다듬습니다.
        c1 = commit1.strip()
        c2 = commit2.strip()

        # [1차]: 출발 커밋 해시의 유효성을 검사합니다.
        # [2차]: 출발역이 지도에 존재하는지 확인합니다.
        if not self.graph.contains(c1):
            raise KeyError(f"Unknown commit: {c1}")
        # [1차]: 도착 커밋 해시의 유효성을 검사합니다.
        # [2차]: 도착역이 지도에 존재하는지 확인합니다.
        if not self.graph.contains(c2):
            raise KeyError(f"Unknown commit: {c2}")

        # [1차]: 그래프 객체의 find_shortest_path 메서드를 호출하여 최단 경로를 반환합니다.
        # [2차]: 내비게이션 엔진을 돌려 최단 길 찾기 결과를 건네줍니다.
        return self.graph.find_shortest_path(c1, c2)

    # [1차]: 특정 커밋의 모든 조상 커밋 객체들을 탐색하여 리스트로 반환합니다.
    # [2차]: 한 사람의 모든 조상님 서류들을 족보에서 모조리 찾아 모아옵니다.
    def ancestors(self, commit_hash: str) -> List[Commit]:
        """Retrieves all ancestor commits of commit_hash."""
        # [1차]: 저장소 초기화 여부를 검사합니다.
        # [2차]: 작업실이 정상적으로 열려있는지 확인합니다.
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        # [1차]: 커밋 해시 문자열의 공백을 제거합니다.
        # [2차]: 조회할 사람의 주민번호 빈칸을 지웁니다.
        ch = commit_hash.strip()
        # [1차]: 대상 커밋이 저장소에 존재하는지 검사합니다.
        # [2차]: 족보에 실제로 등재된 사람인지 확인합니다.
        if not self.graph.contains(ch):
            raise KeyError(f"Unknown commit: {ch}")

        # [1차]: 그래프 모듈의 get_ancestors로 조상 해시 목록을 가져옵니다.
        # [2차]: 가계도를 거슬러 올라가 모든 조상님 번호 목록을 받아옵니다.
        ancestor_hashes = self.graph.get_ancestors(ch)
        # [1차]: Commit 객체들을 담을 결과 리스트입니다.
        # [2차]: 실제 조상님 서류들을 담을 서류 바구니입니다.
        commits: List[Commit] = []
        # [1차]: 각 조상 해시를 순회하며 실제 Commit 객체를 수집합니다.
        # [2차]: 번호표를 하나씩 들고 서랍에서 실제 서류를 찾아 바구니에 담습니다.
        for h in ancestor_hashes:
            c = self.graph.get_commit(h)
            if c is not None:
                commits.append(c)
        # [1차]: 수집된 조상 Commit 객체 리스트를 반환합니다.
        # [2차]: 찾은 모든 조상님 서류들을 제출합니다.
        return commits

    # [1차]: 역색인을 통해 특정 키워드가 포함된 커밋 객체들을 O(1) 시간으로 조회합니다.
    # [2차]: 책 뒤의 단어 색인을 통해 해당 단어가 적힌 모든 커밋 문서를 즉각 찾아냅니다.
    def search_keyword(self, keyword: str) -> List[Commit]:
        """Searches commits containing the given keyword via inverted index."""
        # [1차]: 저장소 초기화 여부를 검사합니다.
        # [2차]: 작업실 문이 열려있는지 확인합니다.
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        # [1차]: 검색 키워드의 앞뒤 공백을 제거합니다.
        # [2차]: 찾고자 하는 단어의 빈칸을 지웁니다.
        kw = keyword.strip()
        # [1차]: 검색어가 비어있을 경우 빈 리스트를 반환합니다.
        # [2차]: 아무 단어도 안 줬다면 아무것도 안 돌려줍니다.
        if not kw:
            return []

        # [1차]: 역색인에서 키워드와 매칭된 커밋 해시 리스트를 O(1)로 가져옵니다.
        # [2차]: 색인 페이지를 단숨에 펴서 적혀있는 번호들을 복사해 옵니다.
        matched_hashes = self.index.search_keyword(kw)
        # [1차]: 일치하는 Commit 객체들을 담을 결과 리스트입니다.
        # [2차]: 찾아낸 서류들을 담을 바구니입니다.
        commits: List[Commit] = []
        # [1차]: 해시 목록을 순회하며 실제 Commit 객체를 모읍니다.
        # [2차]: 번호에 맞는 실제 서류들을 서랍에서 쏙쏙 뽑아 담습니다.
        for h in matched_hashes:
            c = self.graph.get_commit(h)
            if c is not None:
                commits.append(c)
        # [1차]: 매칭된 커밋 객체 리스트를 반환합니다.
        # [2차]: 검색된 모든 결과 서류들을 건네줍니다.
        return commits

    # [1차]: 역색인을 통해 특정 작성자가 작성한 커밋 객체들을 O(1) 시간으로 조회합니다.
    # [2차]: 작가별 색인 서랍을 열어 그 사람이 작성한 모든 커밋 문서를 즉각 찾아냅니다.
    def search_author(self, author: str) -> List[Commit]:
        """Searches commits by the given author via inverted index."""
        # [1차]: 저장소 초기화 여부를 검사합니다.
        # [2차]: 작업실 문이 열려있는지 확인합니다.
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        # [1차]: 작성자 이름의 앞뒤 공백을 제거합니다.
        # [2차]: 찾고자 하는 사람 명찰의 빈칸을 지웁니다.
        auth = author.strip()
        # [1차]: 작성자명이 비어있을 경우 빈 리스트를 반환합니다.
        # [2차]: 빈 명찰을 주면 아무것도 찾지 않습니다.
        if not auth:
            return []

        # [1차]: 역색인에서 작성자명과 매칭된 커밋 해시 리스트를 O(1)로 가져옵니다.
        # [2차]: 작가별 서랍을 열어 그 사람의 커밋 번호표들을 가져옵니다.
        matched_hashes = self.index.search_author(auth)
        # [1차]: Commit 객체들을 담을 결과 리스트입니다.
        # [2차]: 결과 서류 바구니입니다.
        commits: List[Commit] = []
        # [1차]: 해시 목록을 순회하며 실제 Commit 객체를 모읍니다.
        # [2차]: 번호표에 맞춰 실제 서류들을 서랍에서 쏙쏙 챙깁니다.
        for h in matched_hashes:
            c = self.graph.get_commit(h)
            if c is not None:
                commits.append(c)
        # [1차]: 매칭된 커밋 객체 리스트를 반환합니다.
        # [2차]: 그 작가의 모든 작품 서류들을 건네줍니다.
        return commits

    # [1차]: 저장소의 전체 상태와 커밋 목록을 JSON 파일로 직렬화하여 저장합니다.
    # [2차]: 작업실의 모든 현황판과 서랍 속 서류들을 영구 보관 파일로 백업합니다.
    def save_to_json(self, filepath: Optional[str] = None) -> None:
        """Saves repository state and commits to a JSON file."""
        target_path = filepath or self.storage_path
        if not target_path:
            return

        commits_data = [
            {
                "hash": c.hash,
                "message": c.message,
                "author": c.author,
                "timestamp": c.timestamp,
                "parents": c.parents
            }
            for c in self.graph.all_commits()
        ]

        data = {
            "state": {
                "is_initialized": self.state.is_initialized,
                "current_author": self.state.current_author,
                "head_branch": self.state.head_branch,
                "branches": self.state.branches
            },
            "commits": commits_data,
            "commit_counter": self._commit_counter
        }

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # [1차]: JSON 파일로부터 저장소 상태와 커밋들을 역직렬화하여 복원합니다.
    # [2차]: 보관 파일에서 과거 작업 현황판과 모든 서류들을 불러와 서랍과 색인을 채웁니다.
    def load_from_json(self, filepath: Optional[str] = None) -> bool:
        """Loads repository state and commits from a JSON file."""
        target_path = filepath or self.storage_path
        # [1차]: 파일 경로가 없거나 파일이 존재하지 않거나 0바이트 빈 파일이면 False를 반환합니다.
        # [2차]: 서류철이 없거나 텅 빈 백지라면 읽기를 중단합니다.
        if not target_path or not os.path.exists(target_path) or os.path.getsize(target_path) == 0:
            return False

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return False

        state_data = data.get("state", {})
        self.state = RepositoryState(
            is_initialized=state_data.get("is_initialized", False),
            current_author=state_data.get("current_author"),
            head_branch=state_data.get("head_branch"),
            branches=state_data.get("branches", {})
        )

        self.graph = CommitGraph()
        self.index = InvertedIndex()

        commits_data = data.get("commits", [])
        for cd in commits_data:
            c = Commit(
                hash=cd["hash"],
                message=cd["message"],
                author=cd["author"],
                timestamp=cd["timestamp"],
                parents=cd.get("parents", [])
            )
            self.graph.add_commit(c)
            self.index.add_commit(c)

        self._commit_counter = data.get("commit_counter", len(commits_data))
        return True

    # [1차]: 영속화 경로가 설정되어 있는 경우 자동으로 상태를 저장합니다.
    # [2차]: 서류나 현황판에 변동이 생길 때마다 자동으로 백업을 남깁니다.
    def _auto_save(self) -> None:
        """Automatically saves state if storage_path is configured."""
        if self.storage_path:
            self.save_to_json(self.storage_path)
