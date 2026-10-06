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
    def topological_sort(self) -> List[Commit]:
        """Returns all commits in topological order where parents appear before children."""
        # [1차]: 저장된 커밋이 하나도 없으면 빈 리스트를 즉시 반환합니다.
        # [2차]: 족보에 등록된 사람이 아무도 없으면 빈 종이를 돌려줍니다.
        if not self._commits:
            return []

        # [1차]: 부모 -> 자식 연결 관계를 나타내는 인접 리스트 딕셔너리를 초기화합니다.
        # [2차]: 각 부모가 누구누구를 낳았는지 기록할 자식 명단 수첩을 만듭니다.
        children_map: Dict[str, List[str]] = {h: [] for h in self._commits}

        # [1차]: 각 커밋의 진입 차수(in-degree, 선행 부모 수)를 0으로 초기화합니다.
        # [2차]: 각 작업이 시작되기 전에 먼저 끝나야 하는 선행 작업 개수를 0으로 둡니다.
        in_degree: Dict[str, int] = {h: 0 for h in self._commits}

        # [1차]: 모든 커밋을 순회하며 부모-자식 간선과 진입 차수를 집계합니다.
        # [2차]: 가족 서류를 전부 훑어보며 족보 관계와 부모님 수를 파악합니다.
        for commit in self._commits.values():
            # [1차]: 각 커밋이 가리키는 부모 해시들을 순회합니다.
            # [2차]: 이 사람이 가리키는 부모님 명단을 확인합니다.
            for p_hash in commit.parents:
                # [1차]: 부모 해시가 현재 저장소에 실제로 등록되어 있는 경우에만 간선을 연결합니다.
                # [2차]: 부모님이 우리 마을 족보에 등록된 사람인 경우에만 정식으로 연결합니다.
                if p_hash in self._commits:
                    # [1차]: 부모의 자식 목록에 현재 커밋 해시를 추가합니다.
                    # [2차]: 부모님의 자식 목록에 내 이름을 추가합니다.
                    children_map[p_hash].append(commit.hash)
                    # [1차]: 현재 커밋의 진입 차수를 1 증가시킵니다.
                    # [2차]: 내게 필요한 선행 부모 작업 개수를 1개 늘립니다.
                    in_degree[commit.hash] += 1

        # [1차]: 진입 차수가 0인 노드(부모가 없는 최초의 루트 커밋들)를 수집합니다.
        # [2차]: 아무런 준비물 없이 지금 당장 시작할 수 있는 첫 번째 기초 작업들을 골라냅니다.
        ready_hashes: List[str] = [h for h, deg in in_degree.items() if deg == 0]

        # [1차]: 준비된 커밋들의 정렬 기준 키(생성 시점 오름차순, 동률 시 해시 오름차순)를 정의합니다.
        # [2차]: 같은 순서의 작업들이라면 먼저 태어난 순서대로 결정하는 규칙입니다.
        def commit_tie_key(c_hash: str):
            c = self._commits[c_hash]
            return (c.timestamp, c.hash)

        # [1차]: 수제 병합 정렬을 통해 최초 준비 노드들을 결정론적으로 정렬합니다.
        # [2차]: 시작 가능한 작업들을 시간 순서대로 가지런히 줄 세웁니다.
        ready_hashes = merge_sort(ready_hashes, key=commit_tie_key)

        # [1차]: 최종 정렬된 커밋 해시들을 순서대로 담을 결과 리스트입니다.
        # [2차]: 완벽하게 순서가 잡힌 최종 작업 순서표 종이입니다.
        result_hashes: List[str] = []

        # [1차]: 진입 차수가 0이 된 준비 노드가 남아있는 동안 반복 탐색합니다.
        # [2차]: 당장 실행할 수 있는 작업이 남아있는 동안 하나씩 꺼내어 처리합니다.
        while ready_hashes:
            # [1차]: 준비 큐의 맨 앞(가장 빠른) 커밋 해시를 꺼냅니다.
            # [2차]: 대기열 맨 앞의 준비된 작업을 꺼내어 완료 도장을 찍습니다.
            curr_hash = ready_hashes.pop(0)

            # [1차]: 결과 순서표에 현재 커밋 해시를 추가합니다.
            # [2차]: 작업 완료 순서표에 방금 끝낸 작업을 차례대로 적어 넣습니다.
            result_hashes.append(curr_hash)

            # [1차]: 방금 처리한 노드의 자식들 중 새롭게 진입 차수가 0이 된 노드들을 담을 임시 리스트입니다.
            # [2차]: 이번 작업이 끝나서 비로소 시작할 수 있게 된 다음 작업 후보들 바구니입니다.
            newly_ready: List[str] = []

            # [1차]: 방금 꺼낸 커밋의 모든 자식 노드들을 순회합니다.
            # [2차]: 이 부모님 아래에 있는 자식들을 찾아갑니다.
            for child_hash in children_map[curr_hash]:
                # [1차]: 자식 노드의 남은 부모 진입 차수를 1 감소시킵니다.
                # [2차]: 자식에게 필요한 선행 조건 하나가 해결되었음을 표시합니다.
                in_degree[child_hash] -= 1
                # [1차]: 모든 부모가 처리되어 진입 차수가 0이 되면 준비 목록에 추가합니다.
                # [2차]: 모든 선행 작업이 끝났다면 이제 시작할 준비가 완료된 것입니다!
                if in_degree[child_hash] == 0:
                    newly_ready.append(child_hash)

            # [1차]: 새로 준비된 자식 노드들이 있다면 정렬 후 큐에 병합합니다.
            # [2차]: 새롭게 대기열에 들어온 다음 작업들을 시간순으로 기존 대기열과 합칩니다.
            if newly_ready:
                # [1차]: 새로 준비된 노드들을 자체 병합 정렬합니다.
                # [2차]: 새로 들어온 작업들을 먼저 가지런히 정돈합니다.
                newly_ready = merge_sort(newly_ready, key=commit_tie_key)
                # [1차]: 기존 큐와 새 노드들을 합칩니다.
                # [2차]: 기존 줄 뒤에 새 작업들을 붙입니다.
                combined = ready_hashes + newly_ready
                # [1차]: 전체 대기열을 다시 결정론적으로 정렬합니다.
                # [2차]: 합쳐진 전체 줄을 번호순으로 다시 바르게 정돈합니다.
                ready_hashes = merge_sort(combined, key=commit_tie_key)

        # [1차]: 만약 비연결 그래프나 순환 등으로 방문되지 않은 노드가 남았을 경우에 대한 방어 로직입니다.
        # [2차]: 혹시라도 누락된 작업이 있다면 마지막에 안전하게 챙겨둡니다.
        visited_set = set(result_hashes)
        remaining = [h for h in self._commits if h not in visited_set]
        if remaining:
            remaining = merge_sort(remaining, key=commit_tie_key)
            result_hashes.extend(remaining)

        # [1차]: 정렬된 해시들을 실제 Commit 객체 리스트로 매핑하여 반환합니다.
        # [2차]: 완성된 순서표 번호에 맞춰 실제 서류들을 착착 포장해 건넵니다.
        return [self._commits[h] for h in result_hashes]

    # [1차]: 부모-자식 간선을 무방향으로 간주하여 시작 커밋과 목표 커밋 간 최단 경로를 BFS로 탐색합니다.
    # [2차]: 지하철역 사이를 역방향도 탈 수 있는 패스로 가장 적은 환승역을 거쳐가는 경로를 찾습니다.
    def find_shortest_path(self, start_hash: str, end_hash: str) -> Optional[List[str]]:
        """Finds the shortest path between start_hash and end_hash in the undirected graph."""
        # [1차]: 시작 노드나 종료 노드가 저장소에 존재하지 않으면 None을 반환합니다.
        # [2차]: 출발역이나 도착역이 지도에 없으면 길을 찾을 수 없다고 알립니다.
        if start_hash not in self._commits or end_hash not in self._commits:
            return None

        # [1차]: 출발지와 목적지가 동일한 경우 자기 자신으로 구성된 1노드 경로를 즉시 반환합니다.
        # [2차]: 출발역과 도착역이 같으면 이동할 필요 없이 현재 역만 돌려줍니다.
        if start_hash == end_hash:
            return [start_hash]

        # [1차]: 양방향 탐색을 위해 모든 연결을 무방향 인접 집합 맵으로 구성합니다.
        # [2차]: 모든 일방통행 골목길을 양방향 자유 통행 도로망으로 지도에 새로 그립니다.
        adj: Dict[str, Set[str]] = {h: set() for h in self._commits}
        for commit in self._commits.values():
            for p_hash in commit.parents:
                if p_hash in self._commits:
                    # [1차]: 커밋에서 부모로의 경로를 인접 집합에 추가합니다.
                    # [2차]: 자식 집에서 부모님 집으로 가는 길을 연결합니다.
                    adj[commit.hash].add(p_hash)
                    # [1차]: 부모에서 커밋으로의 역방향 경로도 인접 집합에 추가합니다.
                    # [2차]: 부모님 집에서 자식 집으로 되돌아오는 길도 연결합니다.
                    adj[p_hash].add(commit.hash)

        # [1차]: BFS 탐색 경로를 보관할 deque 큐를 생성하고 시작 경로를 삽입합니다.
        # [2차]: 출발점에서 뻗어나갈 탐색 경로들을 담아둘 대기열 바구니를 만듭니다.
        queue: Deque[List[str]] = deque([[start_hash]])

        # [1차]: 각 노드에 도달한 최단 거리(홉 수)를 기록하는 딕셔너리입니다.
        # [2차]: 각 역마다 가장 적게 걸린 이동 정거장 수를 메모해두는 표입니다.
        visited_dist: Dict[str, int] = {start_hash: 0}

        # [1차]: 처음으로 목적지에 도달했을 때의 최소 간선 거리(홉 수)를 저장할 변수입니다.
        # [2차]: 도착역에 처음 도착했을 때 찍힌 최소 정거장 수를 기억할 메모칸입니다.
        target_distance: Optional[int] = None

        # [1차]: 동일한 최단 거리를 가진 모든 도달 경로들을 모아둘 후보군 리스트입니다.
        # [2차]: 같은 최소 정거장 수로 도착한 우수한 경로들을 모아두는 후보 바구니입니다.
        candidate_paths: List[List[str]] = []

        # [1차]: 큐가 빌 때까지 계층별 너비 우선 탐색(BFS)을 수행합니다.
        # [2차]: 탐색할 경로가 남아있는 동안 물결이 퍼져나가듯 한 홉씩 전진합니다.
        while queue:
            # [1차]: 대기열 맨 앞에서 탐색 경로를 하나 꺼냅니다.
            # [2차]: 대기열 맨 앞의 탐색 루트를 꺼내어 발걸음을 옮깁니다.
            path = queue.popleft()

            # [1차]: 현재 경로의 마지막 방문 노드(현재 위치)를 추출합니다.
            # [2차]: 방금 도착한 현재 역의 이름을 확인합니다.
            curr = path[-1]

            # [1차]: 현재 경로의 간선 수(노드 수 - 1)를 계산합니다.
            # [2차]: 출발역부터 여기까지 몇 정거장을 거쳐왔는지 셉니다.
            dist = len(path) - 1

            # [1차]: 이미 발견된 최단 거리보다 더 긴 탐색 경로는 조기 가지치기(Pruning)합니다.
            # [2차]: 이미 찾은 지름길보다 더 멀리 돌아가는 길은 미련 없이 버립니다.
            if target_distance is not None and dist > target_distance:
                break

            # [1차]: 현재 노드가 목적지(end_hash)에 도달한 경우 후보군에 추가합니다.
            # [2차]: 드디어 도착역에 도달했다면 이 경로를 합격자 명단에 등록합니다.
            if curr == end_hash:
                target_distance = dist
                candidate_paths.append(path)
                continue

            # [1차]: 현재 노드와 연결된 모든 이웃 노드들을 순회합니다.
            # [2차]: 현재 역에서 갈아탈 수 있는 모든 다음 역들을 둘러봅니다.
            for neighbor in adj[curr]:
                # [1차]: 다음 노드까지의 간선 거리를 계산합니다.
                # [2차]: 다음 역까지 가면 총 몇 정거장이 되는지 계산합니다.
                neighbor_dist = dist + 1

                # [1차]: 다음 거리가 이미 확정된 최단 거리보다 크면 탐색을 건너뜁니다.
                # [2차]: 다음 걸음이 이미 찾은 최단 거리보다 길어지면 건너뜁니다.
                if target_distance is not None and neighbor_dist > target_distance:
                    continue

                # [1차]: 아직 방문하지 않았거나 동일한 최소 거리로 처음 도달한 경로만 큐에 추가합니다.
                # [2차]: 아직 안 가본 역이거나 똑같은 최단 기록으로 도착한 길만 대기열에 넣습니다.
                if neighbor not in visited_dist or visited_dist[neighbor] == neighbor_dist:
                    visited_dist[neighbor] = neighbor_dist
                    queue.append(path + [neighbor])

        # [1차]: 목적지에 도달 가능한 경로가 전혀 없으면 None을 반환합니다.
        # [2차]: 끊어진 섬처럼 도착역에 갈 수 있는 길이 아예 없다면 없다고 보고합니다.
        if not candidate_paths:
            return None

        # [1차]: 동일한 최단 경로 후보들 중 'hash1->hash2->...' 포맷의 사전순 최소 경로를 선택합니다.
        # [2차]: 정거장 수가 똑같다면 경로 문자열이 가나다순으로 가장 앞서는 예쁜 길을 최종 선정합니다.
        sorted_candidates = merge_sort(
            candidate_paths,
            key=lambda p: "->".join(p)
        )

        # [1차]: 사전순으로 가장 작은 0번째 최단 경로를 반환합니다.
        # [2차]: 1등으로 선정된 최고의 최단 경로를 건네줍니다.
        return sorted_candidates[0]

    # [1차]: 특정 커밋으로부터 부모 포인터를 역추적하여 도달 가능한 모든 조상 커밋 해시를 반환합니다.
    # [2차]: 한 사람의 족보를 거슬러 올라가 부모, 조부모 등 모든 조상님 명단을 빠짐없이 조사합니다.
    def get_ancestors(self, commit_hash: str) -> List[str]:
        """Finds all ancestor commit hashes reachable via parent pointers."""
        # [1차]: 대상 커밋이 저장소에 없으면 빈 리스트를 반환합니다.
        # [2차]: 조사할 사람이 족보에 없으면 빈 명단을 돌려줍니다.
        if commit_hash not in self._commits:
            return []

        # [1차]: 수집된 조상 해시들을 담을 결과 리스트입니다.
        # [2차]: 조상님들의 이름을 적어둘 긴 명단 종이입니다.
        ancestors: List[str] = []

        # [1차]: 중복 방문을 방지하기 위한 해시 집합(Set)입니다.
        # [2차]: 이미 족보에 올린 조상님을 또 올리지 않게 체크하는 도장판입니다.
        visited: Set[str] = set()

        # [1차]: 부모 탐색을 순차적으로 수행할 큐(Queue)입니다.
        # [2차]: 거슬러 올라갈 부모님들을 차례로 적어둘 대기자 명단입니다.
        queue: Deque[str] = deque()

        # [1차]: 시작 커밋 객체를 조회하여 직계 부모들을 큐에 넣습니다.
        # [2차]: 조사의 주인공을 찾아 그의 아버지/어머니 명단을 대기 명단에 올립니다.
        start_commit = self._commits[commit_hash]
        for p in start_commit.parents:
            if p not in visited:
                visited.add(p)
                queue.append(p)

        # [1차]: 큐에 부모 해시가 남아있는 동안 계속 거슬러 올라갑니다.
        # [2차]: 더 윗세대 조상님이 남아있는 동안 계속해서 위로 위로 찾아갑니다.
        while queue:
            # [1차]: 현재 탐색할 조상 해시를 큐에서 꺼냅니다.
            # [2차]: 이번에 확인할 조상님을 대기열에서 모셔옵니다.
            curr_hash = queue.popleft()

            # [1차]: 조상 목록에 현재 해시를 추가합니다.
            # [2차]: 조상님 명단에 이름을 올립니다.
            ancestors.append(curr_hash)

            # [1차]: 해당 조상 커밋이 저장소에 있다면 그 조상의 부모들도 큐에 추가합니다.
            # [2차]: 그 조상님의 부모님(조부모님)도 계신지 확인하여 명단에 이어 올립니다.
            if curr_hash in self._commits:
                for p in self._commits[curr_hash].parents:
                    if p not in visited:
                        visited.add(p)
                        queue.append(p)

        # [1차]: 찾아낸 모든 조상 커밋 해시 리스트를 반환합니다.
        # [2차]: 완성된 가문의 모든 조상님 명단을 제출합니다.
        return ancestors
