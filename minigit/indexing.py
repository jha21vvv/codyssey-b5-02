"""Inverted Index module for Mini Git.

Provides O(1) keyword and author lookup to avoid O(N) full-table scans.
"""

from typing import Dict, List, Set

from minigit.models import Commit


class InvertedIndex:
    """Manages inverted indexes for commit keywords and authors."""

    def __init__(self) -> None:
        self._keyword_index: Dict[str, List[str]] = {}

        self._author_index: Dict[str, List[str]] = {}

    @staticmethod
    def tokenize(message: str) -> List[str]:
        """Extracts normalized lowercase tokens split by whitespace."""
        tokens = message.strip().split()

        return [token.lower() for token in tokens if token]

    def add_commit(self, commit: Commit) -> None:
        """Indexes a new commit into both keyword and author indexes.

        Args:
            commit: Commit instance to index.
        """
        tokens = self.tokenize(commit.message)

        seen_tokens: Set[str] = set()

        for token in tokens:
            if token not in seen_tokens:
                seen_tokens.add(token)

                if token not in self._keyword_index:
                    self._keyword_index[token] = []

                self._keyword_index[token].append(commit.hash)

        author_key = commit.author.strip().lower()

        if author_key not in self._author_index:
            self._author_index[author_key] = []

        if commit.hash not in self._author_index[author_key]:
            self._author_index[author_key].append(commit.hash)

    def search_keyword(self, keyword: str) -> List[str]:
        """Finds all commit hashes associated with a keyword token.

        Time Complexity: O(1) lookup in hash table.

        Args:
            keyword: Word to search.

        Returns:
            List of matching commit hashes (empty list if no match).
        """
        norm = keyword.strip().lower()

        return list(self._keyword_index.get(norm, []))

    def search_author(self, author: str) -> List[str]:
        """Finds all commit hashes associated with an author.

        Time Complexity: O(1) lookup in hash table.

        Args:
            author: Author name to search.

        Returns:
            List of matching commit hashes (empty list if no match).
        """
        norm = author.strip().lower()

        return list(self._author_index.get(norm, []))
