"""Custom sorting algorithm implementation for Mini Git.

Strict Constraint: Built-in Python sorting functions (sorted(), list.sort())
are strictly prohibited. Merge Sort is implemented manually from scratch.
"""

# [1차]: 타입 안전성을 위한 제네릭 및 함수형 타입 어노테이션 도구를 가져옵니다.
# [2차]: 어떤 물건이든 줄 세울 수 있도록 마법 상자(TypeVar)와 기준표(Callable)를 챙깁니다.
from typing import TypeVar, List, Callable, Any, Optional

# [1차]: 임의의 원소 타입을 표현하는 제네릭 타입 변수 T를 선언합니다.
# [2차]: 사과든, 커밋이든, 숫자든 상관없이 담을 수 있는 만능 바구니 라벨입니다.
T = TypeVar("T")


# [1차]: 두 비교 대상 키의 대소 관계를 판정하여 정수(-1, 0, 1)로 반환하는 헬퍼 함수입니다.
# [2차]: 두 물건의 무게를 양팔 저울에 올려 어느 쪽이 무거운지 판정해 주는 심판관입니다.
def _compare(a_key: Any, b_key: Any) -> int:
    """Compares two keys.
    Returns:
        -1 if a_key < b_key
         0 if a_key == b_key
         1 if a_key > b_key
    """
    # [1차]: a_key가 b_key보다 작은 경우 -1을 반환합니다.
    # [2차]: 첫 번째 물건이 더 가벼우면 파란 깃발(-1)을 듭니다.
    if a_key < b_key:
        return -1
    # [1차]: a_key가 b_key보다 큰 경우 1을 반환합니다.
    # [2차]: 첫 번째 물건이 더 무거우면 빨간 깃발(1)을 듭니다.
    elif a_key > b_key:
        return 1
    # [1차]: 두 키의 크기가 동일한 경우 0을 반환합니다.
    # [2차]: 두 물건의 무게가 똑같으면 하얀 깃발(0)을 듭니다.
    return 0


# [1차]: 이미 정렬된 두 개의 서브리스트를 결합하여 하나의 정렬된 리스트로 합치는 병합 함수입니다.
# [2차]: 이미 번호순으로 줄 서 있는 두 줄의 학생들을 번호 순서대로 한 줄로 합치는 과정입니다.
def _merge(
    left: List[T],
    right: List[T],
    key: Callable[[T], Any],
    reverse: bool
) -> List[T]:
    """Merges two sorted lists into a single sorted list.
    Preserves stability by selecting elements from 'left' when keys are equal.
    """
    # [1차]: 두 리스트의 원소들이 순서대로 채워질 새로운 빈 결과 리스트입니다.
    # [2차]: 합쳐진 학생들이 서게 될 새로운 운동장 줄입니다.
    merged: List[T] = []

    # [1차]: 왼쪽 리스트의 현재 비교 위치를 가리키는 정수 포인터 인덱스입니다.
    # [2차]: 왼쪽 줄의 맨 앞 학생을 가리키는 선생님의 왼손 손가락입니다.
    i = 0

    # [1차]: 오른쪽 리스트의 현재 비교 위치를 가리키는 정수 포인터 인덱스입니다.
    # [2차]: 오른쪽 줄의 맨 앞 학생을 가리키는 선생님의 오른손 손가락입니다.
    j = 0

    # [1차]: 왼쪽 리스트의 전체 원소 개수를 캐싱합니다.
    # [2차]: 왼쪽 줄에 서 있는 학생 수를 미리 세어둡니다.
    len_left = len(left)

    # [1차]: 오른쪽 리스트의 전체 원소 개수를 캐싱합니다.
    # [2차]: 오른쪽 줄에 서 있는 학생 수를 미리 세어둡니다.
    len_right = len(right)

    # [1차]: 양쪽 리스트 모두 아직 검사할 원소가 남아있는 동안 반복을 수행합니다.
    # [2차]: 양쪽 줄에 모두 학생이 남아있을 때까지 1대 1 비교를 계속합니다.
    while i < len_left and j < len_right:
        # [1차]: 각 원소에 key 추출 함수를 적용한 후 대소 관계를 비교합니다.
        # [2차]: 양쪽 줄 맨 앞 학생들의 키(또는 번호)를 확인하여 비교합니다.
        cmp = _compare(key(left[i]), key(right[j]))

        # [1차]: 오름차순(기본값) 정렬 분기문입니다.
        # [2차]: 작은 번호가 앞으로 오는 일반적인 줄 서기 규칙입니다.
        if not reverse:
            # [1차]: 왼쪽 원소가 작거나 같을 때(cmp <= 0) 왼쪽 원소를 선택하여 안정성을 유지합니다.
            # [2차]: 번호가 같을 때는 원래 왼쪽에 먼저 서 있던 학생을 먼저 보내주는 배려(안정 정렬)입니다.
            if cmp <= 0:
                merged.append(left[i])
                i += 1
            # [1차]: 오른쪽 원소가 더 작은 경우 오른쪽 원소를 결과에 추가합니다.
            # [2차]: 오른쪽 학생의 번호가 더 작다면 오른쪽 학생을 새 줄에 먼저 세웁니다.
            else:
                merged.append(right[j])
                j += 1
        # [1차]: 내림차순(reverse=True) 정렬 분기문입니다.
        # [2차]: 큰 번호부터 먼저 서는 거꾸로 줄 서기 규칙입니다.
        else:
            # [1차]: 내림차순 시 왼쪽 원소가 크거나 같을 때 왼쪽 원소를 선택합니다.
            # [2차]: 거꾸로 줄 설 때도 점수가 같다면 원래 앞에 서 있던 학생을 우선 배치합니다.
            if cmp >= 0:
                merged.append(left[i])
                i += 1
            # [1차]: 오른쪽 원소가 더 큰 경우 오른쪽 원소를 결과에 추가합니다.
            # [2차]: 오른쪽 학생의 점수가 더 높다면 그 학생을 먼저 새 줄에 세웁니다.
            else:
                merged.append(right[j])
                j += 1

    # [1차]: 왼쪽 리스트에 아직 남아있는 잉여 원소들을 결과 리스트 끝에 순차 추가합니다.
    # [2차]: 오른쪽 줄이 다 끝나고 왼쪽 줄에 남아있는 학생들을 그대로 새 줄 뒤에 이어 붙입니다.
    while i < len_left:
        merged.append(left[i])
        i += 1

    # [1차]: 오른쪽 리스트에 아직 남아있는 잉여 원소들을 결과 리스트 끝에 순차 추가합니다.
    # [2차]: 왼쪽 줄이 다 끝나고 오른쪽 줄에 남아있는 학생들을 그대로 새 줄 뒤에 이어 붙입니다.
    while j < len_right:
        merged.append(right[j])
        j += 1

    # [1차]: 완벽하게 병합된 새로운 정렬 리스트를 반환합니다.
    # [2차]: 가지런하게 한 줄로 완성된 학생 줄을 반환합니다.
    return merged


# [1차]: 내장 정렬 API를 전혀 사용하지 않는 순수 수제 안정 병합 정렬 진입점 함수입니다.
# [2차]: 어떤 목록이 들어와도 반으로 쪼개고 다시 합치며 완벽하게 정렬하는 마법의 분할 정복 기계입니다.
def merge_sort(
    items: List[T],
    key: Optional[Callable[[T], Any]] = None,
    reverse: bool = False
) -> List[T]:
    """Custom stable Merge Sort implementation.

    Complexity:
        - Best Time Complexity: O(N log N)
        - Average Time Complexity: O(N log N)
        - Worst Time Complexity: O(N log N)
        - Space Complexity: O(N)
        - Stability: Stable (preserves original order for equivalent keys)

    Args:
        items: List of elements to sort.
        key: Function to extract a comparison key from each element.
        reverse: If True, sort in descending order.

    Returns:
        A new list with elements sorted according to key and reverse.
    """
    # [1차]: 별도의 키 추출 함수가 전달되지 않은 경우 항등 함수(자기 자신 반환)를 기본값으로 지정합니다.
    # [2차]: 특별한 기준(예: 이름, 날짜)이 없으면 물건 값 그 자체를 기준으로 삼습니다.
    if key is None:
        key = lambda x: x

    # [1차]: 원본 리스트의 부수 효과(Side-effect)를 방지하기 위해 얕은 복사본을 생성합니다.
    # [2차]: 원본 문서를 훼손하지 않기 위해 복사기를 돌려 사본 종이를 준비합니다.
    source: List[T] = list(items)

    # [1차]: 복사된 리스트의 전체 길이(원소 개수)를 구합니다.
    # [2차]: 정렬해야 할 카드가 총 몇 장인지 확인합니다.
    n = len(source)

    # [1차]: 원소가 0개이거나 1개인 경우 이미 정렬된 상태이므로 기저 조건(Base Case)으로 즉시 반환합니다.
    # [2차]: 카드가 1장뿐이면 더 이상 비교할 상대가 없으므로 그대로 돌려줍니다.
    if n <= 1:
        return source

    # [1차]: 리스트의 중앙 인덱스를 계산하여 이등분 위치를 결정합니다.
    # [2차]: 카드 덱을 양손에 정확히 반씩 나누어 쥡니다.
    mid = n // 2

    # [1차]: 왼쪽 절반 슬라이스에 대해 재귀적으로 merge_sort를 호출하여 정렬합니다.
    # [2차]: 왼손에 든 카드 뭉치를 더 작게 쪼개어 정렬을 마칩니다.
    left_sorted = merge_sort(source[:mid], key=key, reverse=reverse)

    # [1차]: 오른쪽 절반 슬라이스에 대해 재귀적으로 merge_sort를 호출하여 정렬합니다.
    # [2차]: 오른손에 든 카드 뭉치를 더 작게 쪼개어 정렬을 마칩니다.
    right_sorted = merge_sort(source[mid:], key=key, reverse=reverse)

    # [1차]: 각각 정렬된 두 개의 서브리스트를 _merge 함수로 합쳐 최종 결과를 반환합니다.
    # [2차]: 가지런히 정렬된 양손의 카드 뭉치를 순서대로 합쳐 하나의 완벽한 덱을 만듭니다.
    return _merge(left_sorted, right_sorted, key=key, reverse=reverse)
