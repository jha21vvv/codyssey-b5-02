"""Script to bundle only the core source codes into NOTEBOOKLM_FULL_SOURCE.txt."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "NOTEBOOKLM_FULL_SOURCE.txt")

SOURCE_FILES = [
    "main.py",
    "minigit/__init__.py",
    "minigit/models.py",
    "minigit/sorting.py",
    "minigit/indexing.py",
    "minigit/graph.py",
    "minigit/repository.py",
    "minigit/cli.py",
]


def read_file(rel_path: str) -> str:
    path = os.path.join(BASE_DIR, rel_path)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def build_source_only():
    chunks = []
    for rel_path in SOURCE_FILES:
        content = read_file(rel_path)
        header = f"# {'='*76}\n# File: {rel_path}\n# {'='*76}"
        chunks.append(f"{header}\n\n{content}\n")

    full_output = "\n".join(chunks)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(full_output)

    print(f"Generated clean source file: {OUTPUT_FILE} ({len(chunks)} files, {len(full_output)} chars)")


if __name__ == "__main__":
    build_source_only()
