"""Unit tests for custom Merge Sort."""

import unittest
from minigit.sorting import merge_sort


class TestMergeSort(unittest.TestCase):
    def test_empty_and_single_element(self):
        self.assertEqual(merge_sort([]), [])
        self.assertEqual(merge_sort([42]), [42])

    def test_integer_sorting(self):
        data = [5, 2, 9, 1, 5, 6]
        expected = [1, 2, 5, 5, 6, 9]
        self.assertEqual(merge_sort(data), expected)

    def test_reverse_sorting(self):
        data = [5, 2, 9, 1, 5, 6]
        expected = [9, 6, 5, 5, 2, 1]
        self.assertEqual(merge_sort(data, reverse=True), expected)

    def test_key_function(self):
        words = ["banana", "pie", "apple", "kiwi"]
        # Sort by length
        sorted_by_len = merge_sort(words, key=len)
        self.assertEqual(sorted_by_len, ["pie", "kiwi", "apple", "banana"])

    def test_stability(self):
        # Pairs where first element is key, second is initial order index
        items = [(1, 'a'), (2, 'b'), (1, 'c'), (2, 'd'), (1, 'e')]
        result = merge_sort(items, key=lambda x: x[0])
        # Elements with key 1 should maintain order 'a', 'c', 'e'
        # Elements with key 2 should maintain order 'b', 'd'
        expected = [(1, 'a'), (1, 'c'), (1, 'e'), (2, 'b'), (2, 'd')]
        self.assertEqual(result, expected)

    def test_string_sorting(self):
        items = ["zebra", "apple", "mango", "banana"]
        self.assertEqual(merge_sort(items), ["apple", "banana", "mango", "zebra"])


if __name__ == "__main__":
    unittest.main()
