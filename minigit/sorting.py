"""Custom sorting algorithm implementation for Mini Git.

Strict Constraint: Built-in Python sorting functions (sorted(), list.sort())
are strictly prohibited. Merge Sort is implemented manually from scratch.
"""

from typing import TypeVar, List, Callable, Any, Optional


T = TypeVar("T")


def _compare(a_key: Any, b_key: Any) -> int:
    """Compares two keys.
    Returns:
        -1 if a_key < b_key
         0 if a_key == b_key
         1 if a_key > b_key
    """
    if a_key < b_key:
        return -1
    elif a_key > b_key:
        return 1
    return 0


def _merge(
    left: List[T],
    right: List[T],
    key: Callable[[T], Any],
    reverse: bool
) -> List[T]:
    """Merges two sorted lists into a single sorted list.
    Preserves stability by selecting elements from 'left' when keys are equal.
    """
    merged: List[T] = []

    i = 0

    j = 0

    len_left = len(left)

    len_right = len(right)

    while i < len_left and j < len_right:
        cmp = _compare(key(left[i]), key(right[j]))

        if not reverse:
            if cmp <= 0:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        else:
            if cmp >= 0:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

    while i < len_left:
        merged.append(left[i])
        i += 1

    while j < len_right:
        merged.append(right[j])
        j += 1

    return merged


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
    if key is None:
        key = lambda x: x

    source: List[T] = list(items)

    n = len(source)

    if n <= 1:
        return source

    mid = n // 2

    left_sorted = merge_sort(source[:mid], key=key, reverse=reverse)

    right_sorted = merge_sort(source[mid:], key=key, reverse=reverse)

    return _merge(left_sorted, right_sorted, key=key, reverse=reverse)
