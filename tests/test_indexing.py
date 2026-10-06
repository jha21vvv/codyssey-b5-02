"""Unit tests for inverted index module."""

import unittest
from minigit.indexing import InvertedIndex
from minigit.models import Commit


class TestInvertedIndex(unittest.TestCase):
    def setUp(self):
        self.index = InvertedIndex()

    def test_tokenize(self):
        msg = "  Fix Bug #104 in Authentication SYSTEM  "
        tokens = InvertedIndex.tokenize(msg)
        self.assertEqual(tokens, ["fix", "bug", "#104", "in", "authentication", "system"])

    def test_add_and_search_keyword(self):
        c1 = Commit(hash="c1", message="Initial commit", author="Alice", timestamp=100.0)
        c2 = Commit(hash="c2", message="Add commit hook", author="Bob", timestamp=200.0)
        c3 = Commit(hash="c3", message="Fix bug in initial setup", author="Alice", timestamp=300.0)

        self.index.add_commit(c1)
        self.index.add_commit(c2)
        self.index.add_commit(c3)

        # "commit" should match c1 and c2
        self.assertEqual(self.index.search_keyword("commit"), ["c1", "c2"])
        # "initial" should match c1 and c3 (case insensitive)
        self.assertEqual(self.index.search_keyword("INITIAL"), ["c1", "c3"])
        # "setup" should match c3
        self.assertEqual(self.index.search_keyword("setup"), ["c3"])
        # non-existent keyword
        self.assertEqual(self.index.search_keyword("database"), [])

    def test_duplicate_words_in_same_message(self):
        c1 = Commit(hash="c1", message="test test test message", author="Alice", timestamp=100.0)
        self.index.add_commit(c1)
        self.assertEqual(self.index.search_keyword("test"), ["c1"])

    def test_search_author(self):
        c1 = Commit(hash="c1", message="first", author="Alice Smith", timestamp=100.0)
        c2 = Commit(hash="c2", message="second", author="Bob Jones", timestamp=200.0)
        c3 = Commit(hash="c3", message="third", author="alice smith", timestamp=300.0)

        self.index.add_commit(c1)
        self.index.add_commit(c2)
        self.index.add_commit(c3)

        # Author search should be case insensitive
        self.assertEqual(self.index.search_author("alice smith"), ["c1", "c3"])
        self.assertEqual(self.index.search_author("ALICE SMITH"), ["c1", "c3"])
        self.assertEqual(self.index.search_author("Bob Jones"), ["c2"])
        self.assertEqual(self.index.search_author("Charlie"), [])


if __name__ == "__main__":
    unittest.main()
