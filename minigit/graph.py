"""Commit Graph algorithms: DAG Topological Sort, BFS Shortest Path, Ancestors.

Zero External Libraries: Implemented entirely using standard Python data structures
and custom merge_sort.
"""

from typing import Dict, List, Set, Optional, Deque

from collections import deque

from minigit.models import Commit

from minigit.sorting import merge_sort


class CommitGraph:
    """Manages DAG traversal and graph exploration on commits."""

    def __init__(self) -> None:
        self._commits: Dict[str, Commit] = {}

    def add_commit(self, commit: Commit) -> None:
        """Adds a commit node into the graph storage."""
        self._commits[commit.hash] = commit

    def get_commit(self, commit_hash: str) -> Optional[Commit]:
        """Retrieves a commit by its hash in O(1) time."""
        return self._commits.get(commit_hash)

    def contains(self, commit_hash: str) -> bool:
        """Checks if a commit hash exists in the repository."""
        return commit_hash in self._commits

    def all_commits(self) -> List[Commit]:
        """Returns all commits currently stored in the graph."""
        return list(self._commits.values())

    def topological_sort(self) -> List[Commit]:
        """Returns all commits in topological order where parents appear before children."""
        if not self._commits:
            return []

        children_map: Dict[str, List[str]] = {h: [] for h in self._commits}

        in_degree: Dict[str, int] = {h: 0 for h in self._commits}

        for commit in self._commits.values():
            for p_hash in commit.parents:
                if p_hash in self._commits:
                    children_map[p_hash].append(commit.hash)
                    in_degree[commit.hash] += 1

        ready_hashes: List[str] = [h for h, deg in in_degree.items() if deg == 0]

        def commit_tie_key(c_hash: str):
            c = self._commits[c_hash]
            return (c.timestamp, c.hash)

        ready_hashes = merge_sort(ready_hashes, key=commit_tie_key)

        result_hashes: List[str] = []

        while ready_hashes:
            curr_hash = ready_hashes.pop(0)

            result_hashes.append(curr_hash)

            newly_ready: List[str] = []

            for child_hash in children_map[curr_hash]:
                in_degree[child_hash] -= 1
                if in_degree[child_hash] == 0:
                    newly_ready.append(child_hash)

            if newly_ready:
                newly_ready = merge_sort(newly_ready, key=commit_tie_key)
                combined = ready_hashes + newly_ready
                ready_hashes = merge_sort(combined, key=commit_tie_key)

        visited_set = set(result_hashes)
        remaining = [h for h in self._commits if h not in visited_set]
        if remaining:
            remaining = merge_sort(remaining, key=commit_tie_key)
            result_hashes.extend(remaining)


        return [self._commits[h] for h in result_hashes]

    def find_shortest_path(self, start_hash: str, end_hash: str) -> Optional[List[str]]:
        """Finds the shortest path between start_hash and end_hash in the undirected graph."""
        if start_hash not in self._commits or end_hash not in self._commits:
            return None

        if start_hash == end_hash:
            return [start_hash]

        adj: Dict[str, Set[str]] = {h: set() for h in self._commits}
        for commit in self._commits.values():
            for p_hash in commit.parents:
                if p_hash in self._commits:
                    adj[commit.hash].add(p_hash)
                    adj[p_hash].add(commit.hash)

        queue: Deque[List[str]] = deque([[start_hash]])

        visited_dist: Dict[str, int] = {start_hash: 0}

        target_distance: Optional[int] = None

        candidate_paths: List[List[str]] = []

        while queue:
            path = queue.popleft()

            curr = path[-1]

            dist = len(path) - 1

            if target_distance is not None and dist > target_distance:
                break

            if curr == end_hash:
                target_distance = dist
                candidate_paths.append(path)
                continue

            for neighbor in adj[curr]:
                neighbor_dist = dist + 1

                if target_distance is not None and neighbor_dist > target_distance:
                    continue


                if neighbor not in visited_dist or visited_dist[neighbor] == neighbor_dist:
                    visited_dist[neighbor] = neighbor_dist
                    queue.append(path + [neighbor])

        if not candidate_paths:
            return None

        sorted_candidates = merge_sort(
            candidate_paths,
            key=lambda p: "->".join(p)
        )

        return sorted_candidates[0]

    def get_ancestors(self, commit_hash: str) -> List[str]:
        """Finds all ancestor commit hashes reachable via parent pointers."""
        if commit_hash not in self._commits:
            return []

        ancestors: List[str] = []

        visited: Set[str] = set()

        queue: Deque[str] = deque()

        start_commit = self._commits[commit_hash]
        for p in start_commit.parents:
            if p not in visited:
                visited.add(p)
                queue.append(p)

        while queue:
            curr_hash = queue.popleft()

            ancestors.append(curr_hash)

            if curr_hash in self._commits:
                for p in self._commits[curr_hash].parents:
                    if p not in visited:
                        visited.add(p)
                        queue.append(p)

        return ancestors
