"""Tests for find_introducing_commits / simplified SZZ (T-103).

Builds throwaway git repositories in tmp_path to test:
1. Standard fixture: commit B plants bug, commit C fixes it -> points to B and right lines.
2. Whitespace fixture: commit B plants bug, commit W reformats whitespace only,
   commit C fixes bug -> git blame -w skips W and points to B.
3. Addition-only fix commit: fix only adds lines, removes nothing -> returns empty list.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from devreview.dataset.szz import BuggyLocation, find_introducing_commits

# ── helpers ──────────────────────────────────────────────────────────────────


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "user.email", "test@test.com")
    return repo


def _commit_file(repo: Path, filename: str, content: str, message: str) -> str:
    path = repo / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    _git(repo, "add", filename)
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


# ── tests ────────────────────────────────────────────────────────────────────


def test_fixture_plants_and_fixes_bug(tmp_path: Path) -> None:
    """Commit B plants a bug, commit C fixes it -> points to B with correct lines."""
    repo = _init_repo(tmp_path)

    # Initial commit A
    _commit_file(
        repo,
        "calc.py",
        "def add(a, b):\n    return a + b\n",
        "initial commit",
    )

    # Commit B: plants a bug on divide function
    sha_b = _commit_file(
        repo,
        "calc.py",
        "def add(a, b):\n    return a + b\n\ndef divide(a, b):\n    return a * b  # BUG: should be /\n",
        "add divide function",
    )

    # Commit C: fixes the bug
    sha_c = _commit_file(
        repo,
        "calc.py",
        "def add(a, b):\n    return a + b\n\ndef divide(a, b):\n    return a / b\n",
        "fix divide function bug",
    )

    locations = find_introducing_commits(str(repo), sha_c)

    assert len(locations) == 1
    loc = locations[0]
    assert loc.introducing_sha == sha_b
    assert loc.file == "calc.py"
    # In commit B, line 5 is "    return a * b  # BUG: should be /"
    assert loc.start_line == 5
    assert loc.end_line == 5


def test_whitespace_intermediate_commit_skipped(tmp_path: Path) -> None:
    """Whitespace-only commit W between bug B and fix C is skipped via blame -w."""
    repo = _init_repo(tmp_path)

    # Initial commit A
    _commit_file(
        repo,
        "utils.py",
        "def greet(name):\n    pass\n",
        "initial commit",
    )

    # Commit B: plants buggy logic
    sha_b = _commit_file(
        repo,
        "utils.py",
        "def greet(name):\n    msg = 'Hello' + name  # BUG: missing space\n    return msg\n",
        "implement greet",
    )

    # Commit W: whitespace reformat only (e.g. extra spaces / indentation change)
    _commit_file(
        repo,
        "utils.py",
        "def greet(name):\n      msg = 'Hello' + name  # BUG: missing space\n      return msg\n",
        "reformat whitespace in utils",
    )

    # Commit C: fixes the bug
    sha_c = _commit_file(
        repo,
        "utils.py",
        "def greet(name):\n      msg = 'Hello ' + name\n      return msg\n",
        "fix greeting space",
    )

    locations = find_introducing_commits(str(repo), sha_c)

    assert len(locations) == 1
    loc = locations[0]
    assert loc.introducing_sha == sha_b
    assert loc.file == "utils.py"
    assert loc.start_line == 2
    assert loc.end_line == 2


def test_addition_only_fix_returns_empty(tmp_path: Path) -> None:
    """A fix commit that only appends new lines has no removed lines to blame."""
    repo = _init_repo(tmp_path)

    _commit_file(
        repo,
        "app.py",
        "print('start')\n",
        "initial commit",
    )

    # Commit C: fix that only appends error handling
    sha_c = _commit_file(
        repo,
        "app.py",
        "print('start')\nprint('safe shutdown')\n",
        "fix missing shutdown log",
    )

    locations = find_introducing_commits(str(repo), sha_c)
    assert locations == []


def test_buggy_location_dict_and_attr_access() -> None:
    """BuggyLocation supports both attribute and dict-like key access."""
    loc = BuggyLocation(
        introducing_sha="abc123",
        file="foo.py",
        start_line=10,
        end_line=15,
    )
    assert loc.introducing_sha == "abc123"
    assert loc["introducing_sha"] == "abc123"
    assert loc["file"] == "foo.py"
    assert loc["start_line"] == 10
    assert loc["end_line"] == 15
    assert loc.to_dict() == {
        "introducing_sha": "abc123",
        "file": "foo.py",
        "start_line": 10,
        "end_line": 15,
    }
