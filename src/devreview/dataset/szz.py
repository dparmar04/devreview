"""Simplified SZZ algorithm to find bug-introducing commits from git history.

Given a bug-fix commit F, simplified SZZ:
1. Diff F against its parent P (F^) using ``git diff -U0`` to find deleted or modified lines.
2. For each deleted/modified line range, blame P using ``git blame --porcelain -w -L <start>,<end>``.
   - ``-w`` ignores whitespace-only commits.
   - In porcelain output, the 2nd number on the header line is the line number inside
     the introducing commit.
3. Groups contiguous lines from the same introducing commit into ``BuggyLocation`` records.
"""

from __future__ import annotations

import re
import subprocess  # nosec: B404  # required by spec; no git library allowed
from dataclasses import asdict, dataclass
from typing import Any

_HUNK_HEADER_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


@dataclass(frozen=True)
class BuggyLocation:
    """Represents a code region identified as bug-introducing by SZZ."""

    introducing_sha: str
    file: str
    start_line: int
    end_line: int

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _run_git(repo_path: str, args: list[str]) -> str:
    """Run a git command in *repo_path* and return its stdout."""
    result = subprocess.run(  # nosec: B603, B607  # fixed args, no user input
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _parse_diff_deleted_ranges(diff_text: str) -> list[tuple[str, int, int]]:
    """Parse ``git diff -U0`` output and return list of ``(file, start_line, end_line)`` in parent."""
    ranges: list[tuple[str, int, int]] = []
    current_old_file: str | None = None

    for line in diff_text.splitlines():
        if line.startswith("--- "):
            raw_path = line[4:].strip()
            if raw_path == "/dev/null":
                current_old_file = None
            elif raw_path.startswith("a/"):
                current_old_file = raw_path[2:]
            else:
                current_old_file = raw_path
        elif line.startswith("@@ "):
            if current_old_file is None:
                continue
            match = _HUNK_HEADER_RE.match(line)
            if not match:
                continue
            old_start = int(match.group(1))
            old_count = int(match.group(2)) if match.group(2) is not None else 1
            if old_count > 0:
                old_end = old_start + old_count - 1
                ranges.append((current_old_file, old_start, old_end))

    return ranges


def _blame_range(
    repo_path: str,
    parent_sha: str,
    file_path: str,
    start_line: int,
    end_line: int,
) -> list[tuple[str, int]]:
    """Run git blame --porcelain -w on parent for line range and return list of (sha, line_in_introducing)."""
    line_spec = f"{start_line},{end_line}"
    stdout = _run_git(
        repo_path,
        [
            "blame",
            "--porcelain",
            "-w",
            "-L",
            line_spec,
            parent_sha,
            "--",
            file_path,
        ],
    )

    blamed_lines: list[tuple[str, int]] = []
    for line in stdout.splitlines():
        # Header lines format: <sha:40> <orig_line> <final_line> [<group_count>]
        tokens = line.split()
        if len(tokens) >= 3 and len(tokens[0]) == 40 and tokens[1].isdigit() and tokens[2].isdigit():
            sha = tokens[0]
            orig_line = int(tokens[1])
            blamed_lines.append((sha, orig_line))

    return blamed_lines


def find_introducing_commits(repo_path: str, fix_sha: str) -> list[BuggyLocation]:
    """Identify the bug-introducing commits and line ranges for a given fix commit.

    Parameters
    ----------
    repo_path:
        Path to local git repository.
    fix_sha:
        Full or partial SHA of the fix commit.

    Returns
    -------
    list[BuggyLocation]
        List of locations in the introducing commits where buggy lines originated.
    """
    # Parent commit of fix
    parent_sha = _run_git(repo_path, ["rev-parse", f"{fix_sha}^"]).strip()

    diff_output = _run_git(
        repo_path,
        ["diff", "-U0", f"{fix_sha}^", fix_sha],
    )

    deleted_ranges = _parse_diff_deleted_ranges(diff_output)
    locations: list[BuggyLocation] = []

    for file_path, start_line, end_line in deleted_ranges:
        blamed = _blame_range(repo_path, parent_sha, file_path, start_line, end_line)
        if not blamed:
            continue

        # Group consecutive lines with the same introducing sha
        cur_sha, cur_start = blamed[0]
        cur_end = cur_start

        for sha, orig_line in blamed[1:]:
            if sha == cur_sha and orig_line == cur_end + 1:
                cur_end = orig_line
            else:
                loc = BuggyLocation(
                    introducing_sha=cur_sha,
                    file=file_path,
                    start_line=cur_start,
                    end_line=cur_end,
                )
                if loc not in locations:
                    locations.append(loc)
                cur_sha, cur_start, cur_end = sha, orig_line, orig_line

        loc = BuggyLocation(
            introducing_sha=cur_sha,
            file=file_path,
            start_line=cur_start,
            end_line=cur_end,
        )
        if loc not in locations:
            locations.append(loc)

    return locations
