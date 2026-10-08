"""MiniGit repository management logic."""

import json
import os

import hashlib

import time

from typing import List, Optional, Tuple, Dict

from minigit.models import Commit, RepositoryState

from minigit.graph import CommitGraph

from minigit.indexing import InvertedIndex

from minigit.sorting import merge_sort


class MiniGitRepository:
    """Core domain repository orchestrating models, indexing, sorting, and graph queries."""

    def __init__(self, storage_path: Optional[str] = None) -> None:
        self.state = RepositoryState()
        self.graph = CommitGraph()
        self.index = InvertedIndex()
        self._commit_counter = 0
        self.storage_path = storage_path

        if self.storage_path and os.path.exists(self.storage_path):
            self.load_from_json(self.storage_path)

    def is_initialized(self) -> bool:
        """Checks if repository has been initialized via INIT."""
        return self.state.is_initialized

    def init(self, user_name: str) -> str:
        """Initializes a new Mini Git repository."""
        user_name = user_name.strip()
        if not user_name:
            raise ValueError("Invalid args: user_name cannot be empty")

        self.state = RepositoryState(
            is_initialized=True,
            current_author=user_name,
            head_branch="main",
            branches={"main": None}
        )
        self.graph = CommitGraph()
        self.index = InvertedIndex()
        self._commit_counter = 0

        self._auto_save()

        return f"Initialized empty Mini Git repository for {user_name}. Switched to branch 'main'."

    def branch(self, branch_name: str) -> str:
        """Creates a new branch pointing to current HEAD commit."""
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        branch_name = branch_name.strip()
        if not branch_name:
            raise ValueError("Invalid args: branch_name cannot be empty")

        if branch_name in self.state.branches:
            raise ValueError(f"Branch already exists: {branch_name}")

        current_head_commit = self._get_head_commit_hash()
        self.state.branches[branch_name] = current_head_commit
        self._auto_save()
        return f"Created branch '{branch_name}' at {current_head_commit or '(initial)'}."

    def switch(self, branch_name: str) -> str:
        """Switches HEAD to the specified branch."""
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        branch_name = branch_name.strip()
        if not branch_name:
            raise ValueError("Invalid args: branch_name cannot be empty")

        if branch_name in self.state.branches:
            self.state.head_branch = branch_name
            self._auto_save()
            return f"Switched to branch '{branch_name}'."

        raise KeyError(f"Unknown branch: {branch_name}")

    def _generate_unique_hash(self, message: str, author: str, ts: float, parents: List[str]) -> str:
        """Generates a collision-resistant short hash for a new commit."""
        self._commit_counter += 1
        raw_seed = f"{self._commit_counter}:{ts}:{author}:{message}:{','.join(parents)}"
        full_hash = hashlib.sha1(raw_seed.encode("utf-8")).hexdigest()
        candidate = full_hash[:8]
        if self.graph.contains(candidate):
            candidate = full_hash[:12]
        return candidate

    def commit(self, message: str) -> Tuple[Commit, str]:
        """Creates a new commit on current HEAD branch and updates indexes."""
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        message = message.strip()
        if not message:
            raise ValueError("Invalid args: commit message cannot be empty")

        author = self.state.current_author or "Unknown"
        ts = time.time()

        parent_hash = self._get_head_commit_hash()
        parents = [parent_hash] if parent_hash else []

        commit_hash = self._generate_unique_hash(message, author, ts, parents)
        new_commit = Commit(
            hash=commit_hash,
            message=message,
            author=author,
            timestamp=ts,
            parents=parents
        )

        self.graph.add_commit(new_commit)

        self.index.add_commit(new_commit)

        if self.state.head_branch is not None:
            self.state.branches[self.state.head_branch] = commit_hash

        self._auto_save()

        msg = f"[{self.state.head_branch} {commit_hash}] {message}"
        return new_commit, msg

    def _get_head_commit_hash(self) -> Optional[str]:
        """Returns the commit hash currently referenced by HEAD branch."""
        if not self.state.head_branch:
            return None
        return self.state.branches.get(self.state.head_branch)

    def log(self, sort_by: Optional[str] = None) -> List[Commit]:
        """Returns commits according to LOG specification."""
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        if sort_by is None:
            return self.graph.topological_sort()

        all_c = self.graph.all_commits()

        if sort_by == "date":
            return merge_sort(all_c, key=lambda c: c.timestamp)
        elif sort_by == "author":
            return merge_sort(all_c, key=lambda c: c.author.lower())
        else:
            raise ValueError(f"Invalid args: unknown sort option '{sort_by}'")

    def path(self, commit1: str, commit2: str) -> Optional[List[str]]:
        """Calculates undirected shortest path between commit1 and commit2."""
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        c1 = commit1.strip()
        c2 = commit2.strip()

        if not self.graph.contains(c1):
            raise KeyError(f"Unknown commit: {c1}")
        if not self.graph.contains(c2):
            raise KeyError(f"Unknown commit: {c2}")

        return self.graph.find_shortest_path(c1, c2)

    def ancestors(self, commit_hash: str) -> List[Commit]:
        """Retrieves all ancestor commits of commit_hash."""
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        ch = commit_hash.strip()
        if not self.graph.contains(ch):
            raise KeyError(f"Unknown commit: {ch}")

        ancestor_hashes = self.graph.get_ancestors(ch)
        commits: List[Commit] = []
        for h in ancestor_hashes:
            c = self.graph.get_commit(h)
            if c is not None:
                commits.append(c)
        return commits

    def search_keyword(self, keyword: str) -> List[Commit]:
        """Searches commits containing the given keyword via inverted index."""
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        kw = keyword.strip()
        if not kw:
            return []

        matched_hashes = self.index.search_keyword(kw)
        commits: List[Commit] = []
        for h in matched_hashes:
            c = self.graph.get_commit(h)
            if c is not None:
                commits.append(c)
        return commits

    def search_author(self, author: str) -> List[Commit]:
        """Searches commits by the given author via inverted index."""
        if not self.state.is_initialized:
            raise RuntimeError("Repository not initialized")

        auth = author.strip()
        if not auth:
            return []

        matched_hashes = self.index.search_author(auth)
        commits: List[Commit] = []
        for h in matched_hashes:
            c = self.graph.get_commit(h)
            if c is not None:
                commits.append(c)
        return commits

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

    def load_from_json(self, filepath: Optional[str] = None) -> bool:
        """Loads repository state and commits from a JSON file."""
        target_path = filepath or self.storage_path
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

    def _auto_save(self) -> None:
        """Automatically saves state if storage_path is configured."""
        if self.storage_path:
            self.save_to_json(self.storage_path)
