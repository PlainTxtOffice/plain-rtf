"""Report developer identifiers in compiled distribution files."""

# ruff: noqa: INP001
from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path

SCAN_SUFFIXES = {
    ".exe",
    ".dll",
    ".pyd",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".txt",
    ".env",
}


def _look_file_hits(
    path: Path,
    patterns: list[tuple[str, bytes]],
) -> set[str]:
    """Read a binary in bounded chunks and return matching identifier names."""
    overlap = max(len(pattern) for _, pattern in patterns) - 1
    found: set[str] = set()
    with path.open("rb") as stream:
        tail = b""
        while chunk := stream.read(1024 * 1024):
            block = tail + chunk
            found.update(
                label for label, pattern in patterns if pattern in block
            )
            tail = block[-overlap:] if overlap else b""
    return found


def scan_output(repo_root: Path, dist_path: Path) -> list[str]:
    """Read distribution files and report UTF-8 and UTF-16LE identity hits.

    - Includes DLLs because Windows onefile can use a DLL payload.
    - Raises FileNotFoundError when the unpacked distribution is absent.
    - Reports matches without altering files or treating matches as errors.
    """
    if not dist_path.is_dir():
        msg = f"Missing Nuitka distribution: {dist_path}"
        raise FileNotFoundError(msg)
    metadata = tomllib.loads(
        (repo_root / "pyproject.toml").read_text(encoding="utf-8"),
    )
    identifiers = {
        os.environ.get("USERNAME", ""),
        str(repo_root.resolve()),
        repo_root.resolve().as_posix(),
        *(
            author.get("email", "")
            for author in metadata["project"].get("authors", [])
        ),
    } - {""}
    patterns = [
        (identifier, identifier.encode(encoding))
        for identifier in sorted(identifiers)
        for encoding in ("utf-8", "utf-16le")
    ]
    hits = []
    for path in sorted(dist_path.rglob("*")):
        if path.is_file() and (
            path.suffix.lower() in SCAN_SUFFIXES or path.name == ".env"
        ):
            hits.extend(
                f"Privacy scan: {label!r} found in {path}"
                for label in sorted(_look_file_hits(path, patterns))
            )
    return hits


if __name__ == "__main__":
    for message in scan_output(Path(sys.argv[1]), Path(sys.argv[2])):
        sys.stdout.write(f"{message}\n")
