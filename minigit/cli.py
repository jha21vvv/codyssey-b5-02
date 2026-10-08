"""CLI REPL interface and command dispatcher for Mini Git."""

import sys

import shlex

import time

from typing import Optional

from minigit.repository import MiniGitRepository

from minigit.models import Commit


def format_commit(commit: Commit) -> str:
    """Formats a single commit for display.
    Guarantees hash, author, timestamp, message are identifiable.
    """
    ts_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(commit.timestamp))
    parents_str = ", ".join(commit.parents) if commit.parents else "(root)"
    lines = [
        f"commit {commit.hash}",
        f"Author:    {commit.author}",
        f"Date:      {ts_str} ({commit.timestamp:.2f})",
        f"Parents:   {parents_str}",
        f"    {commit.message}"
    ]
    return "\n".join(lines)


class MiniGitCLI:
    """REPL CLI controller."""

    def __init__(self, repo: Optional[MiniGitRepository] = None, storage_path: Optional[str] = None) -> None:
        self.repo = repo if repo is not None else MiniGitRepository(storage_path=storage_path)

    def execute_line(self, line: str) -> Optional[str]:
        """Parses and executes a single CLI command string."""
        line = line.strip()
        if not line:
            return None

        try:
            tokens = shlex.split(line)
        except ValueError as e:
            return f"Invalid args: parsing quotes failed ({e})"

        if not tokens:
            return None

        cmd = tokens[0].upper()
        args = tokens[1:]

        try:
            if cmd == "INIT":
                if len(args) != 1:
                    return "Invalid args: INIT requires <user_name>"
                return self.repo.init(args[0])

            elif cmd == "BRANCH":
                if len(args) != 1:
                    return "Invalid args: BRANCH requires <branch_name>"
                return self.repo.branch(args[0])

            elif cmd == "SWITCH":
                if len(args) != 1:
                    return "Invalid args: SWITCH requires <branch_name>"
                return self.repo.switch(args[0])

            elif cmd == "COMMIT":
                if len(args) != 1:
                    return "Invalid args: COMMIT requires <message>"
                _, msg = self.repo.commit(args[0])
                return msg

            elif cmd == "LOG":
                sort_by = None
                if len(args) == 1:
                    opt = args[0]
                    if opt.startswith("--sort-by="):
                        val = opt.split("=", 1)[1].strip()
                        if val not in ("date", "author"):
                            return "Invalid args: --sort-by must be date or author"
                        sort_by = val
                    else:
                        return "Invalid args: unknown option for LOG"
                elif len(args) > 1:
                    return "Invalid args: LOG accepts at most one --sort-by option"

                commits = self.repo.log(sort_by=sort_by)
                if not commits:
                    return "No commits found."
                return "\n\n".join(format_commit(c) for c in commits)

            elif cmd == "PATH":
                if len(args) != 2:
                    return "Invalid args: PATH requires <commit1> <commit2>"
                path = self.repo.path(args[0], args[1])
                if path is None:
                    return "No path"
                return " -> ".join(path)

            elif cmd == "ANCESTORS":
                if len(args) != 1:
                    return "Invalid args: ANCESTORS requires <commit_hash>"
                ancestors = self.repo.ancestors(args[0])
                if not ancestors:
                    return "No ancestors."
                return "\n\n".join(format_commit(c) for c in ancestors)

            elif cmd == "SEARCH":
                if len(args) != 1:
                    return "Invalid args: SEARCH requires <keyword> or --author=<name>"
                target = args[0]
                if target.startswith("--author="):
                    author_name = target.split("=", 1)[1].strip()
                    if not author_name:
                        return "Invalid args: --author requires a name"
                    commits = self.repo.search_author(author_name)
                else:
                    commits = self.repo.search_keyword(target)

                if not commits:
                    return "No commits found."
                return "\n\n".join(format_commit(c) for c in commits)

            elif cmd in ("EXIT", "QUIT"):
                return "BYE"

            else:
                return f"Invalid args: unknown command '{tokens[0]}'"

        except RuntimeError as e:
            return str(e)
        except KeyError as e:
            err_msg = str(e).strip("'\"")
            return err_msg
        except ValueError as e:
            return str(e)

    def run_repl(self) -> None:
        """Starts the interactive CLI REPL session."""
        print("Mini Git CLI v1.0.0 (Type 'exit' or 'quit' to close)")
        if self.repo.is_initialized():
            print(f"[*] Loaded repository for '{self.repo.state.current_author}' on branch '{self.repo.state.head_branch}'")
        while True:
            try:
                line = input("mini-git> ")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting Mini Git.")
                break

            output = self.execute_line(line)
            if output == "BYE":
                print("Exiting Mini Git.")
                break
            elif output is not None:
                print(output)
