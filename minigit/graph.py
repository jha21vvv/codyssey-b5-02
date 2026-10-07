"""Commit Graph algorithms: DAG Topological Sort, BFS Shortest Path, Ancestors.

Zero External Libraries: Implemented entirely using standard Python data structures
and custom merge_sort.
"""

# [1차]: 타입 힌팅을 위한 제네릭 컬렉션 및 큐 타입을 가져옵니다.
# [2차]: 그래프 길 찾기 지도와 탐색용 대기열 바구니의 명찰들을 준비합니다.
from typing import Dict, List, Set, Optional, Deque

# [1차]: 양방향에서 O(1) 삽입/삭제가 가능한 collections 모듈의 deque를 가져옵니다.
# [2차]: 줄 선 순서대로 빠르게 빠져나갈 수 있는 고속 놀이공원 대기열(줄서기)을 준비합니다.
from collections import deque

# [1차]: 커밋 데이터 모델 클래스를 가져옵니다.
# [2차]: 그래프의 각 정점(노드)이 될 커밋 명찰을 가져옵니다.
from minigit.models import Commit

# [1차]: 정렬 API 금지 규칙에 따라 수제 구현한 안정 병합 정렬 함수를 가져옵니다.
# [2차]: 외장 도구 없이 자체 제작한 튼튼한 정렬 기계를 장착합니다.
from minigit.sorting import merge_sort


# [1차]: 커밋 DAG의 저장 및 위상 정렬, BFS 최단 경로, 조상 탐색을 총괄하는 그래프 클래스입니다.
# [2차]: 얽히고설킨 족보와 골목길 지도를 펼쳐놓고 길을 찾아주는 내비게이션 본부입니다.
class CommitGraph:
    """Manages DAG traversal and graph exploration on commits."""

    # [1차]: 그래프 저장소를 초기화하는 생성자입니다.
    # [2차]: 새로운 지도판을 책상 위에 깨끗이 펼칩니다.
    def __init__(self) -> None:
        # [1차]: 커밋 해시 문자열을 키로, Commit 객체를 값으로 갖는 해시맵 저장소입니다.
        # [2차]: 커밋 해시(주민번호)만 대면 즉시 커밋 정보를 꺼낼 수 있는 보관 서랍장입니다.
        self._commits: Dict[str, Commit] = {}

    # [1차]: 새로운 커밋 노드를 그래프 내부 해시맵에 등록합니다.
    # [2차]: 새롭게 태어난 가족의 이름과 서류를 족보 서랍에 등록합니다.
    def add_commit(self, commit: Commit) -> None:
        """Adds a commit node into the graph storage."""
        # [1차]: 커밋 객체의 해시를 키로 저장소에 할당합니다.
        # [2차]: 서랍 칸에 커밋 주민번호 명찰을 붙여 보관합니다.
        self._commits[commit.hash] = commit

    # [1차]: 커밋 해시로 커밋 객체를 O(1) 시간에 조회합니다.
    # [2차]: 주민번호를 건네받아 서랍 속 서류를 단숨에 꺼내옵니다.
    def get_commit(self, commit_hash: str) -> Optional[Commit]:
        """Retrieves a commit by its hash in O(1) time."""
        # [1차]: dict.get()으로 안전하게 조회하여 없으면 None을 반환합니다.
        # [2차]: 서랍을 찾아보고 서류가 없으면 빈손으로 돌아옵니다.
        return self._commits.get(commit_hash)

    # [1차]: 특정 커밋 해시가 저장소에 존재하는지 여부를 확인합니다.
    # [2차]: 이 서랍장에 해당 번호의 서류가 들어있는지 유무를 확인합니다.
    def contains(self, commit_hash: str) -> bool:
        """Checks if a commit hash exists in the repository."""
        # [1차]: 'in' 연산자로 딕셔너리 키 존재 여부를 판정합니다.
        # [2차]: 명단에 이름이 적혀있는지 출석 체크를 합니다.
        return commit_hash in self._commits

    # [1차]: 현재 저장된 모든 커밋 객체들의 리스트를 반환합니다.
    # [2차]: 서랍장에 들어있는 모든 서류들을 한꺼번에 꺼내놓습니다.
    def all_commits(self) -> List[Commit]:
        """Returns all commits currently stored in the graph."""
        # [1차]: 딕셔너리의 values를 리스트로 변환하여 반환합니다.
        # [2차]: 서랍 속 물건들을 모두 바구니에 담아 건넵니다.
        return list(self._commits.values())

    # [1차]: 부모 커밋이 항상 자식 커밋보다 먼저 출력되도록 Kahn의 알고리즘 기반 위상 정렬을 수행합니다.
    # [2차]: 요리 레시피 순서처럼 기초 재료 준비(부모)가 끝나야 다음 요리(자식)를 하는 순서표를 만듭니다.
    # [3차 예시 기준]: 커밋 A(부모 없음) ─┬─> B(부모 A)
    #                                  └─> C(부모 A) ──> D(부모 C) 구조를 기준으로 한 줄씩 추적합니다.
    def topological_sort(self) -> List[Commit]:
        """Returns all commits in topological order where parents appear before children."""
        # [1차]: 저장된 커밋이 하나도 없으면 빈 리스트를 즉시 반환합니다.
        # [2차]: 족보에 등록된 사람이 아무도 없으면 빈 종이를 돌려줍니다.
        # [3차 예시]: self._commits에 A, B, C, D가 들어있으므로 통과하고 다음 줄로 이동합니다.
        if not self._commits:
            return []

        # [1차]: 부모 -> 자식 연결 관계를 나타내는 인접 리스트 딕셔너리를 초기화합니다.
        # [2차]: 각 부모가 누구누구를 낳았는지 기록할 자식 명단 수첩을 만듭니다.
        # [3차 예시]: children_map = {'A': [], 'B': [], 'C': [], 'D': []} (모두 빈 리스트로 초기화)
        children_map: Dict[str, List[str]] = {h: [] for h in self._commits}

        # [1차]: 각 커밋의 진입 차수(in-degree, 선행 부모 수)를 0으로 초기화합니다.
        # [2차]: 각 작업이 시작되기 전에 먼저 끝나야 하는 선행 작업 개수를 0으로 둡니다.
        # [3차 예시]: in_degree = {'A': 0, 'B': 0, 'C': 0, 'D': 0} (모두 0으로 초기화)
        in_degree: Dict[str, int] = {h: 0 for h in self._commits}

        # [1차]: 모든 커밋을 순회하며 부모-자식 간선과 진입 차수를 집계합니다.
        # [2차]: 가족 서류를 전부 훑어보며 족보 관계와 부모님 수를 파악합니다.
        # [3차 예시]: 커밋 A, B, C, D를 하나씩 꺼내어 parents를 검사합니다.
        for commit in self._commits.values():
            # [1차]: 각 커밋이 가리키는 부모 해시들을 순회합니다.
            # [2차]: 이 사람이 가리키는 부모님 명단을 확인합니다.
            # [3차 예시]: A는 부모 없음, B는 ['A'], C는 ['A'], D는 ['C']가 전달됩니다.
            for p_hash in commit.parents:
                # [1차]: 부모 해시가 현재 저장소에 실제로 등록되어 있는 경우에만 간선을 연결합니다.
                # [2차]: 부모님이 우리 마을 족보에 등록된 사람인 경우에만 정식으로 연결합니다.
                # [3차 예시]: 부모인 'A'와 'C'가 모두 저장소에 등록되어 있으므로 조건 충족.
                if p_hash in self._commits:
                    # [1차]: 부모의 자식 목록에 현재 커밋 해시를 추가합니다.
                    # [2차]: 부모님의 자식 목록에 내 이름을 추가합니다.
                    # [3차 예시]: children_map['A']에 B, C가 추가되고, children_map['C']에 D가 추가됨.
                    #            -> children_map 결과: {'A': ['B', 'C'], 'B': [], 'C': ['D'], 'D': []}
                    children_map[p_hash].append(commit.hash)
                    # [1차]: 현재 커밋의 진입 차수를 1 증가시킵니다.
                    # [2차]: 내게 필요한 선행 부모 작업 개수를 1개 늘립니다.
                    # [3차 예시]: in_degree 결과: {'A': 0, 'B': 1, 'C': 1, 'D': 1} (A는 0, 나머지는 1)
                    in_degree[commit.hash] += 1

        # [1차]: 진입 차수가 0인 노드(부모가 없는 최초의 루트 커밋들)를 수집합니다.
        # [2차]: 아무런 준비물 없이 지금 당장 시작할 수 있는 첫 번째 기초 작업들을 골라냅니다.
        # [3차 예시]: in_degree가 0인 유일한 커밋 'A'만 추출됨 -> ready_hashes = ['A']
        ready_hashes: List[str] = [h for h, deg in in_degree.items() if deg == 0]

        # [1차]: 준비된 커밋들의 정렬 기준 키(생성 시점 오름차순, 동률 시 해시 오름차순)를 정의합니다.
        # [2차]: 같은 순서의 작업들이라면 먼저 태어난 순서대로 결정하는 규칙입니다.
        # [3차 예시]: 동일 우선순위일 때 생성 시간(timestamp) 순서로 줄을 세우는 함수를 정의합니다.
        def commit_tie_key(c_hash: str):
            c = self._commits[c_hash]
            return (c.timestamp, c.hash)

        # [1차]: 수제 병합 정렬을 통해 최초 준비 노드들을 결정론적으로 정렬합니다.
        # [2차]: 시작 가능한 작업들을 시간 순서대로 가지런히 줄 세웁니다.
        # [3차 예시]: ready_hashes에 ['A'] 하나뿐이므로 정렬 후에도 ['A'].
        # 마이: commit_tie_key를 넣은 이유: 컴퓨터는 커밋 내용이나 시간을 전혀 모르고, 그냥 **알파벳 순서('a' 다음 'f')**로만 줄을 세워버립니다.
        # 하지만 우리는 **"실제로 먼저 만들어진 커밋(시간 순서)"**대로 내보내고 싶습니다.
        ready_hashes = merge_sort(ready_hashes, key=commit_tie_key)

        # [1차]: 최종 정렬된 커밋 해시들을 순서대로 담을 결과 리스트입니다.
        # [2차]: 완벽하게 순서가 잡힌 최종 작업 순서표 종이입니다.
        # [3차 예시]: result_hashes = [] (최종 출력 바구니 생성)
        result_hashes: List[str] = []

        # [1차]: 진입 차수가 0이 된 준비 노드가 남아있는 동안 반복 탐색합니다.
        # [2차]: 당장 실행할 수 있는 작업이 남아있는 동안 하나씩 꺼내어 처리합니다.
        # [3차 예시]: ready_hashes에 ['A']가 있으므로 while문 1회전 시작!
        # 여기가 중요함. 레디 해쉬들중 하나를 커런트 해쉬로 데려가서 정리하는거
        while ready_hashes:
            # [1차]: 준비 큐의 맨 앞(가장 빠른) 커밋 해시를 꺼냅니다.
            # [2차]: 대기열 맨 앞의 준비된 작업을 꺼내어 완료 도장을 찍습니다.
            # [3차 예시]: (1회전) curr_hash = 'A' 꺼냄 -> ready_hashes = []
            curr_hash = ready_hashes.pop(0)

            # [1차]: 결과 순서표에 현재 커밋 해시를 추가합니다.
            # [2차]: 작업 완료 순서표에 방금 끝낸 작업을 차례대로 적어 넣습니다.
            # [3차 예시]: (1회전) result_hashes = ['A'] (1등으로 A 확정!)
            result_hashes.append(curr_hash)

            # [1차]: 방금 처리한 노드의 자식들 중 새롭게 진입 차수가 0이 된 노드들을 담을 임시 리스트입니다.
            # [2차]: 이번 작업이 끝나서 비로소 시작할 수 있게 된 다음 작업 후보들 바구니입니다.
            # [3차 예시]: (1회전) newly_ready = [] 초기화
            newly_ready: List[str] = []

            # [1차]: 방금 꺼낸 커밋의 모든 자식 노드들을 순회합니다.
            # [2차]: 이 부모님 아래에 있는 자식들을 찾아갑니다.
            # [3차 예시]: (1회전) 'A'의 자식인 children_map['A'] = ['B', 'C'] 순회 시작
            for child_hash in children_map[curr_hash]:
                # [1차]: 자식 노드의 남은 부모 진입 차수를 1 감소시킵니다.
                # [2차]: 자식에게 필요한 선행 조건 하나가 해결되었음을 표시합니다.
                # [3차 예시]: (1회전) in_degree['B'](1->0), in_degree['C'](1->0) 1씩 깎임! (D는 A의 자식이 아니므로 여전히 1)
                in_degree[child_hash] -= 1
                # [1차]: 모든 부모가 처리되어 진입 차수가 0이 되면 준비 목록에 추가합니다.
                # [2차]: 모든 선행 작업이 끝났다면 이제 시작할 준비가 완료된 것입니다!
                # [3차 예시]: (1회전) 'B'와 'C' 모두 0이 되었으므로 newly_ready = ['B', 'C'] 에 진입!
                if in_degree[child_hash] == 0:
                    newly_ready.append(child_hash)

            # [1차]: 새로 준비된 자식 노드들이 있다면 정렬 후 큐에 병합합니다.
            # [2차]: 새롭게 대기열에 들어온 다음 작업들을 시간순으로 기존 대기열과 합칩니다.
            # [3차 원리 보장]:
            #   Q. 여기서 ready_hashes와 newly_ready를 합쳐서 다시 정렬하면 자식이 부모보다 앞설 위험은 없나요?
            #   A. 전혀 없습니다!
            #      1) 이번 자식의 부모(curr_hash)는 이미 128번 줄에서 result_hashes에 최종 확정되어 나갔습니다.
            #      2) 따라서 combined 대기열 안에는 이번 자식의 부모가 아예 없습니다!
            #      3) combined에 함께 서 있는 노드들은 서로 부모-자식이 아닌 '사촌(다른 브랜치)' 관계이므로,
            #         이들끼리 시간순 정렬을 해도 부모->자식 인과율은 절대 깨지지 않습니다.
            if newly_ready:
                # [1차]: 새로 준비된 노드들을 자체 병합 정렬합니다.
                # [2차]: 새로 들어온 작업들을 먼저 가지런히 정돈합니다.
                # [3차 예시]: B와 C를 시간순 정렬 -> ['B', 'C']
                newly_ready = merge_sort(newly_ready, key=commit_tie_key)
                # [1차]: 기존 큐와 새 노드들을 합칩니다.
                # [2차]: 기존 줄 뒤에 새 작업들을 붙입니다.
                # [3차 예시]: ready_hashes([]) + newly_ready(['B', 'C']) = ['B', 'C']
                combined = ready_hashes + newly_ready
                # [1차]: 전체 대기열을 다시 결정론적으로 정렬합니다.
                # [2차]: 합쳐진 전체 줄을 번호순으로 다시 바르게 정돈합니다.
                # [3차 예시]: ready_hashes = ['B', 'C']
                #            👉 다음 2회전에서 'B'가 빠져나가 result=['A', 'B']가 됨
                #            👉 다음 3회전에서 'C'가 빠져나가 result=['A', 'B', 'C']가 되고, C 덕분에 D의 in_degree(1->0)가 깎여 ready_hashes=['D']가 됨!
                #            👉 다음 4회전에서 'D'가 빠져나가 result=['A', 'B', 'C', 'D'] 완성!
                ready_hashes = merge_sort(combined, key=commit_tie_key)

        # [1차]: 만약 비연결 그래프나 순환 등으로 방문되지 않은 노드가 남았을 경우에 대한 방어 로직입니다.
        # [2차]: 혹시라도 누락된 작업이 있다면 마지막에 안전하게 챙겨둡니다.
        # [3차 예시]: A, B, C, D 모두 result_hashes에 들어가 있으므로 remaining = [] (통과)
        visited_set = set(result_hashes)
        remaining = [h for h in self._commits if h not in visited_set]
        if remaining:
            remaining = merge_sort(remaining, key=commit_tie_key)
            result_hashes.extend(remaining)

            '''
            요약하면,
            모든 커밋을 데려와서 그중에 남은 업무가 0인 애들만 레디 해쉬로 데려와
            레디 해쉬에서 하나를 커런트 해쉬로 데려가서 정리
            정리가 끝나면 커런트 해쉬의 자식들의 남은 업무를 1씩 깎아줘
            그리고 자식들의 업무가 다 깎여서 0이라면 뉴리 레디해쉬로 데려와
            뉴리 레디 해쉬와 남은 레디 해쉬를 합쳐서 재 정렬해서 컴바인을 만들어
            컴바인을 새로운 레디 해쉬로 지정해
            레디 해쉬로 다시 위의 반복 작업을 해

            이 과정을 반복하다 보면 레디 해쉬가 빌때가 오는데 그럼 반복문이 끝나
            
            그래서 리저트에 있는애들은 처리한거니 비지티드 세트가 되고
            남은 애들은 리메이닝이 돼. 
            리메이닝을 정렬후에 리저트 마지막에 추가하는 형태야.
            '''

        # [1차]: 정렬된 해시들을 실제 Commit 객체 리스트로 매핑하여 반환합니다.
        # [2차]: 완성된 순서표 번호에 맞춰 실제 서류들을 착착 포장해 건넵니다.
        # [3차 예시]: 최종 반환: [Commit('A'), Commit('B'), Commit('C'), Commit('D')] 순서로 반환!
        return [self._commits[h] for h in result_hashes]

    # [1차]: 부모-자식 간선을 무방향으로 간주하여 시작 커밋과 목표 커밋 간 최단 경로를 BFS로 탐색합니다.
    # [2차]: 지하철역 사이를 역방향도 탈 수 있는 패스로 가장 적은 환승역을 거쳐가는 경로를 찾습니다.
    # [3차 예시 기준]: 커밋 A ─┬─> B (main)
    #                        └─> C ──> D (feature) 에서 start_hash='B', end_hash='D' 탐색을 추적합니다.
    def find_shortest_path(self, start_hash: str, end_hash: str) -> Optional[List[str]]:
        """Finds the shortest path between start_hash and end_hash in the undirected graph."""
        # [1차]: 시작 노드나 종료 노드가 저장소에 존재하지 않으면 None을 반환합니다.
        # [2차]: 출발역이나 도착역이 지도에 없으면 길을 찾을 수 없다고 알립니다.
        # [3차 예시]: 'B'와 'D' 모두 저장소에 존재하므로 통과합니다.
        if start_hash not in self._commits or end_hash not in self._commits:
            return None

        # [1차]: 출발지와 목적지가 동일한 경우 자기 자신으로 구성된 1노드 경로를 즉시 반환합니다.
        # [2차]: 출발역과 도착역이 같으면 이동할 필요 없이 현재 역만 돌려줍니다.
        # [3차 예시]: start_hash('B') != end_hash('D')이므로 통과합니다.
        if start_hash == end_hash:
            return [start_hash]

        # [1차]: 양방향 탐색을 위해 모든 연결을 무방향 인접 집합 맵으로 구성합니다.
        # [2차]: 모든 일방통행 골목길을 양방향 자유 통행 도로망으로 지도에 새로 그립니다.
        # [3차 예시]: adj = {'A': set(), 'B': set(), 'C': set(), 'D': set()} 생성
        adj: Dict[str, Set[str]] = {h: set() for h in self._commits}
        for commit in self._commits.values():
            for p_hash in commit.parents:
                if p_hash in self._commits:
                    # [1차]: 커밋에서 부모로의 경로를 인접 집합에 추가합니다.
                    # [2차]: 자식 집에서 부모님 집으로 가는 길을 연결합니다.
                    # [3차 예시]: B->A, C->A, D->C 방향 길을 추가합니다.
                    adj[commit.hash].add(p_hash)
                    # [1차]: 부모에서 커밋으로의 역방향 경로도 인접 집합에 추가합니다.
                    # [2차]: 부모님 집에서 자식 집으로 되돌아오는 길도 연결합니다.
                    # [3차 예시]: A->B, A->C, C->D 반대 방향 길도 추가합니다.
                    #            -> 완성된 adj: {'A': {'B', 'C'}, 'B': {'A'}, 'C': {'A', 'D'}, 'D': {'C'}}
                    adj[p_hash].add(commit.hash)
                    # 마이: ㅈ같이 설명해놨는데 위에꺼는 나 해쉬[부모 해쉬]구조로 만든거고
                    #아래는 부모 해쉬에[내 해쉬]를 넣은 구조임.

        # [1차]: BFS 탐색 경로를 보관할 deque 큐를 생성하고 시작 경로를 삽입합니다.
        # [2차]: 출발점에서 뻗어나갈 탐색 경로들을 담아둘 대기열 바구니를 만듭니다.
        # [3차 예시]: queue = deque([['B']]) ('B'에서 출발하는 첫 번째 경로 리스트를 
        # 큐에 투입)
        # 마이 대문자 데큐는 "이 변수(queue)는 데크 형식이고, 그 안에는 ['B', 'A'] 같은
        # 리스트들이 들어갈 거야!"**라고 미리 알려주는 설명용 라벨
        #소문자 deque (진짜 객체 생성자):파이썬 내장 모듈(collections)에서 지원하는
        #*`*실제 데크 자료형을 메모리에 새로 만들어내는 진짜 클래스(공장)*
        '''
        #deque([
        #    ["B", "A"],         # B에서 A로 간 경로
        #    ["B", "A", "C"],    # B -> A -> C로 간 경로
        #    ["B", "A", "C", "D"]# B -> A -> C -> D로 간 경로
        #])
        이렇게 생긴게 들어가게 됨.
        '''
        queue: Deque[List[str]] = deque([[start_hash]])

        # [1차]: 각 노드에 도달한 최단 거리(홉 수)를 기록하는 딕셔너리입니다.
        # [2차]: 각 역마다 가장 적게 걸린 이동 정거장 수를 메모해두는 표입니다.
        # [3차 예시]: visited_dist = {'B': 0} (출발점 B까지의 거리는 0)
        visited_dist: Dict[str, int] = {start_hash: 0}

        # [1차]: 처음으로 목적지에 도달했을 때의 최소 간선 거리(홉 수)를 저장할 변수입니다.
        # [2차]: 도착역에 처음 도착했을 때 찍힌 최소 정거장 수를 기억할 메모칸입니다.
        # [3차 예시]: target_distance = None (아직 D에 도착 못 함)
        target_distance: Optional[int] = None

        # [1차]: 동일한 최단 거리를 가진 모든 도달 경로들을 모아둘 후보군 리스트입니다.
        # [2차]: 같은 최소 정거장 수로 도착한 우수한 경로들을 모아두는 후보 바구니입니다.
        # [3차 예시]: candidate_paths = [] (도착 경로 후보 바구니)
        candidate_paths: List[List[str]] = []

        # [1차]: 큐가 빌 때까지 계층별 너비 우선 탐색(BFS)을 수행합니다.
        # [2차]: 탐색할 경로가 남아있는 동안 물결이 퍼져나가듯 한 홉씩 전진합니다.
        while queue:
            # [1차]: 대기열 맨 앞에서 탐색 경로를 하나 꺼냅니다.
            # [2차]: 대기열 맨 앞의 탐색 루트를 꺼내어 발걸음을 옮깁니다.
            # [3차 예시]: (1회전) path = ['B'] 꺼냄
            # 마이: 최초에는 아무 자료 없이 queue: Deque[List[str]] = deque([[start_hash]])만 있기에
            # 그냥 스타트 해쉬가 나오는 상황
            path = queue.popleft()

            # [1차]: 현재 경로의 마지막 방문 노드(현재 위치)를 추출합니다.
            # [2차]: 방금 도착한 현재 역의 이름을 확인합니다.
            # [3차 예시]: (1회전) curr = 'B'
            # 마이: 최초에는 똑같이 start_hash가 들어감. 한개 뿐이라 -1이란 인덱스 효과가 없는거
            curr = path[-1]

            # [1차]: 현재 경로의 간선 수(노드 수 - 1)를 계산합니다.
            # [2차]: 출발역부터 여기까지 몇 정거장을 거쳐왔는지 셉니다.
            # [3차 예시]: (1회전) dist = len(['B']) - 1 = 0
            dist = len(path) - 1

            # [1차]: 이미 발견된 최단 거리보다 더 긴 탐색 경로는 조기 가지치기(Pruning)합니다.
            # [2차]: 이미 찾은 지름길보다 더 멀리 돌아가는 길은 미련 없이 버립니다.
            # [3차 예시]: (1회전) 아직 target_distance가 None이므로 통과
            # 이미 한계 거리까지 시도해본거면 스탑 가능하게 해둔거.
            if target_distance is not None and dist > target_distance:
                break

            # [1차]: 현재 노드가 목적지(end_hash)에 도달한 경우 후보군에 추가합니다.
            # [2차]: 드디어 도착역에 도달했다면 이 경로를 합격자 명단에 등록합니다.
            # [3차 예시]: (1회전) curr('B') != end_hash('D')이므로 통과
            # 마이: 모든길로 1칸씩 가기에 제일먼저 도착지에 도착한게 가장 빠른 길이다.
            if curr == end_hash:
                # 마이: 그러고 나서 이걸 타겟 디스턴스로 했기에 이것 과 같을때만 진행되고 아니면 전부 반려 되도록 이프절이 있는 구조이다.
                target_distance = dist
                candidate_paths.append(path)
                continue

            # [1차]: 현재 노드와 연결된 모든 이웃 노드들을 순회합니다.
            # [2차]: 현재 역에서 갈아탈 수 있는 모든 다음 역들을 둘러봅니다.
            # [3차 예시]: (1회전) adj['B'] = {'A'} 순회 시작
            for neighbor in adj[curr]:
                # [1차]: 다음 노드까지의 간선 거리를 계산합니다.
                # [2차]: 다음 역까지 가면 총 몇 정거장이 되는지 계산합니다.
                # [3차 예시]: (1회전) neighbor_dist = 0 + 1 = 1 (A까지 1정거장)
                neighbor_dist = dist + 1

                # [1차]: 다음 거리가 이미 확정된 최단 거리보다 크면 탐색을 건너뜁니다.
                # [2차]: 다음 걸음이 이미 찾은 최단 거리보다 길어지면 건너뜁니다.
                # 와일에 따라 다음 방안으로 시도한다는 이야기
                if target_distance is not None and neighbor_dist > target_distance:
                    continue

                # [1차]: 아직 방문하지 않았거나 동일한 최소 거리로 처음 도달한 경로만 큐에 추가합니다.
                # [2차]: 아직 안 가본 역이거나 똑같은 최단 기록으로 도착한 길만 대기열에 넣습니다.
                # [3차 예시]: (1회전) 'A'는 처음 방문! -> visited_dist['A'] = 1 기록, queue에 ['B', 'A'] 추가
                #            👉 (2회전) path=['B', 'A'] 꺼냄 -> 이웃 'C' 방문 -> queue에 ['B', 'A', 'C'] 추가 (dist=2)
                #            👉 (3회전) path=['B', 'A', 'C'] 꺼냄 -> 이웃 'D' 방문 -> queue에 ['B', 'A', 'C', 'D'] 추가 (dist=3)
                #            👉 (4회전) path=['B', 'A', 'C', 'D'] 꺼냄 -> curr='D' 도착!
                #                       target_distance = 3 확정, candidate_paths에 ['B', 'A', 'C', 'D'] 저장!
                # neighbor_dist에 대해 이해하신 내용("이번 이웃으로 이동했을 때의 총 거리
                # for neighbor in adj[curr]
                # 역에 도착했을 때 **"이 역까지 몇 정거장 걸렸는지 적어두는 기록 장부(딕셔너리)"

                # neighbor not in visited_dist (장부에 아직 이름이 없나?
                # visited_dist[neighbor] == neighbor_dist (이미 적혀있다면?):장부에 이미 적혀있긴 한데... 
                # 장부에 적힌 기록(visited_dist[neighbor])과 지금 내 기록(neighbor_dist)이 **똑같은 거리(동점)*네? 너도 합격!"

                # 이 상황자체가 길을 이어붙이는 케이스임. 즉 빙 둘러오는 루투가 발생하여 거리가 더 길수 있음.
                # 기존 길보다 길면 탈락하면서 이어붙이기 케이스에서 실패하는셈.
                # 즉 중간 경유지까지 오는 방식별로 거리를 계산해서 최단거리를 계산할수 있게 한셈.
                if neighbor not in visited_dist or visited_dist[neighbor] == neighbor_dist:
                    visited_dist[neighbor] = neighbor_dist
                    queue.append(path + [neighbor])
                    '''
                    path = ["B", "A"]        # 지금까지 온 길
                    neighbor = "C"           # 이번에 새로 밟은 다음 역

                    path + [neighbor]        # ["B", "A"] + ["C"]
                    # 👉 결과: ["B", "A", "C"] (출발부터 지금까지의 전체 경로 완성!)

                    '''

        # [1차]: 목적지에 도달 가능한 경로가 전혀 없으면 None을 반환합니다.
        # [2차]: 끊어진 섬처럼 도착역에 갈 수 있는 길이 아예 없다면 없다고 보고합니다.
        # [3차 예시]: candidate_paths에 경로가 있으므로 통과합니다.
        if not candidate_paths:
            return None

        # [1차]: 동일한 최단 경로 후보들 중 'hash1->hash2->...' 포맷의 사전순 최소 경로를 선택합니다.
        # [2차]: 정거장 수가 똑같다면 경로 문자열이 가나다순으로 가장 앞서는 예쁜 길을 최종 선정합니다.
        # [3차 예시]: 최단 경로가 여러 개일 경우 'B->A->C->D' 문자열 기준 사전순 정렬
        sorted_candidates = merge_sort(
            candidate_paths,
            key=lambda p: "->".join(p)
        )

        # [1차]: 사전순으로 가장 작은 0번째 최단 경로를 반환합니다.
        # [2차]: 1등으로 선정된 최고의 최단 경로를 건네줍니다.
        # [3차 예시]: 최종 반환: ['B', 'A', 'C', 'D'] (B에서 A로 올라갔다가 C 거쳐 D로 도착하는 3홉 최단 경로)
        return sorted_candidates[0]

    # [1차]: 특정 커밋으로부터 부모 포인터를 역추적하여 연결된 모든 과거 조상 커밋 해시를 반환합니다.
    # [2차]: '내 커밋'에서 출발해 직속 부모 -> 부모의 부모 -> 최초 루트 커밋까지 과거 이력을 연쇄 추적(BFS)합니다.
    # [3차 예시 기준]: 커밋 A ─┬─> B
    #                        └─> C ──> D 에서 commit_hash = 'D'의 조상을 찾는 과정을 추적합니다.
    def get_ancestors(self, commit_hash: str) -> List[str]:
        """Finds all ancestor commit hashes reachable via parent pointers."""
        # [1차]: 대상 커밋이 저장소에 없으면 빈 리스트를 반환합니다.
        # [2차]: 존재하지 않는 커밋 해시가 들어오면 바로 빈 결과를 반환해 에러를 방지합니다.
        # [3차 예시]: 'D'가 저장소에 존재하므로 통과합니다.
        if commit_hash not in self._commits:
            return []

        # [1차]: 탐색 과정에서 발견된 모든 조상 커밋 해시를 순서대로 누적할 결과 리스트입니다.
        # [2차]: "찾아낸 과거 커밋들"을 차곡차곡 담아둘 최종 바구니입니다.
        # [3차 예시]: ancestors = [] (결과 바구니 초기화)
        ancestors: List[str] = []

        # [1차]: 머지(Merge) 커밋 등으로 인해 동일한 부모를 중복 방문하거나 무한 루프에 빠지는 것을 막는 집합(Set)입니다.
        # [2차]: "이미 확인한 커밋 해시 목록"입니다. 중복 검사와 무한 루프를 O(1) 속도로 차단합니다.
        # [3차 예시]: visited = set() (방문 세트 초기화)
        visited: Set[str] = set()

        # [1차]: 너비 우선 탐색(BFS) 방식으로 부모들을 세대별로 차례차례 꺼내기 위한 선입선출(FIFO) 큐입니다.
        # [2차]: "다음에 부모를 타고 올라갈 커밋 대기열"입니다.
        # [3차 예시]: queue = deque() (탐색 대기열 생성)
        queue: Deque[str] = deque()

        # [1차]: 시작 커밋의 직속 부모(1세대 위)들을 먼저 큐와 방문 세트에 등록합니다.
        # [2차]: 탐색 시작: 내 바로 위 직속 부모들을 대기열(queue)에 1순위로 집어넣습니다.
        # [3차 예시]: 'D'의 부모는 ['C'] 하나뿐 -> visited = {'C'}, queue = deque(['C'])
        start_commit = self._commits[commit_hash]
        # 일단 최초로 페어런츠들을 큐에 넣음. 그리고 비지티드에 넣음
        for p in start_commit.parents:
            if p not in visited:
                visited.add(p)
                queue.append(p)

        # [1차]: 큐에 조사할 부모 커밋이 남아있는 동안, 과거로 꼬리를 물며 계속 거슬러 올라갑니다.
        # [2차]: 대기열에 과거 커밋이 남아있다면 계속 루프를 돌며 윗 세대를 추적합니다.
        # [3차 예시]: queue에 ['C']가 있으므로 while문 1회전 시작!
        while queue:
            # [1차]: 대기열의 맨 앞(가장 가까운 세대) 커밋 해시를 하나 꺼냅니다.
            # [2차]: 대기열 맨 앞에서 커밋 하나를 꺼냅니다.
            # [3차 예시]: (1회전) curr_hash = 'C' 꺼냄 -> queue = deque([])
            # 해당 큐에 있는 애중 첫번째에를 데리고 나옴
            curr_hash = queue.popleft()

            # [1차]: 현재 꺼낸 커밋을 최종 조상 결과 목록에 추가합니다.
            # [2차]: 이 커밋은 조상으로 판명되었으니 결과 바구니에 담습니다.
            # [3차 예시]: (1회전) ancestors = ['C'] (D의 첫 번째 조상 발견!)
            # 걔는 앤세스터에 바로 넣음
            #2번째로 올때 부모의 부모를 앤세스터에 넣는셈
            ancestors.append(curr_hash)

            # [1차]: 꺼낸 커밋의 부모(한 세대 더 위)들을 조회하여 아직 방문하지 않은 부모를 큐에 연쇄 등록합니다.
            # [2차]: "방금 확인한 커밋의 부모(한 단계 더 과거 커밋)"가 있다면, 걔들도 대기열에 새로 추가합니다.
            # [3차 예시]: (1회전) 'C'의 부모 self._commits['C'].parents = ['A'] 확인!
            #            'A'는 미방문이므로 visited에 {'C', 'A'} 등록, queue에 'A' 투입 -> queue = deque(['A'])
            #            👉 (2회전) curr_hash = 'A' 꺼냄 -> ancestors = ['C', 'A'] (두 번째 조상 발견!)
            #            👉 'A'의 부모는 [] (루트이므로 없음) -> queue가 텅 비어서 while문 종료!
            if curr_hash in self._commits:
                # 걔의 페어런츠들을 가지고 와서 
                for p in self._commits[curr_hash].parents:
                    # 마이: 비지티드를 모은 이유. 두번 비지티드에 갈수 없도록 한것
                    '''
                           커밋 A (뿌리)
                           /       \
                       커밋 B     커밋 C  (가지)
                           \       /
                           커밋 M (머지 커밋! 부모가 B와 C 둘 다임)

                        M의 직속 부모인 **B**와 **C**를 큐에 넣습니다.
                        B 차례: B의 부모인 **A**를 큐에 넣습니다. 👉 큐: [C, A]
                        C 차례: C의 부모를 봅니다. 어? C의 부모도 **A**네?
                        만약 visited가 없다면?
                        👉 큐에 A를 또 집어넣습니다! 큐: [A, A]
                        이걸로 이프절이 없으면 무한루프에 빠지는걸 알 수있다.
                    '''
                    # 비지티드랑 큐에 넣음.
                    if p not in visited:
                        visited.add(p)
                        queue.append(p)

        # [1차]: 모든 부모 역추적이 완료되면 수집된 전체 조상 커밋 리스트를 반환합니다.
        # [2차]: 직속 부모부터 최초 루트 커밋까지 수집된 모든 과거 커밋 리스트를 반환합니다.
        # [3차 예시]: 최종 반환: ['C', 'A'] (D의 조상은 C와 A!)
        return ancestors
