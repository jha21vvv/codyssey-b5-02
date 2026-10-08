"""Domain models for Mini Git."""

from dataclasses import dataclass, field

from typing import List, Dict, Optional


@dataclass
class Commit:
    """Represents an immutable commit node in the commit DAG.

    Attributes:
        hash: Unique commit identifier (hex string).
        message: Commit message describing the changes.
        author: Name of the commit author.
        timestamp: Epoch timestamp (float seconds) when the commit was created.
        parents: List of parent commit hashes (0 or more).
    """
    hash: str
    message: str
    author: str
    timestamp: float
    parents: List[str] = field(default_factory=list)


@dataclass
class RepositoryState:
    """Represents the mutable state of the repository session."""
    is_initialized: bool = False
    current_author: Optional[str] = None
    head_branch: Optional[str] = None
    branches: Dict[str, Optional[str]] = field(default_factory=dict)
