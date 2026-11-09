"""Tests for dataset building and case validation (T-104)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from devreview.dataset.builder import (
    Case,
    build_dataset,
    read_dataset,
    validate_case,
)

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


def test_build_dataset_from_fixture(tmp_path: Path) -> None:
    """Build dataset from fixture repo and verify reading it back identically."""
    repo = _init_repo(tmp_path)

    # Initial commit A (root commit)
    _commit_file(repo, "calc.py", "def add(a, b):\n    return a + b\n", "initial commit")

    # Commit B: introduces a bug (multiply instead of divide)
    sha_b = _commit_file(
        repo,
        "calc.py",
        "def add(a, b):\n    return a + b\n\ndef divide(a, b):\n    return a * b  # BUG\n",
        "add divide function",
    )

    # Commit C: fixes the bug
    sha_c = _commit_file(
        repo,
        "calc.py",
        "def add(a, b):\n    return a + b\n\ndef divide(a, b):\n    return a / b\n",
        "fix divide function bug",
    )

    # Commit D: clean non-buggy feature commit
    sha_d = _commit_file(
        repo,
        "calc.py",
        "def add(a, b):\n    return a + b\n\ndef divide(a, b):\n    return a / b\n\ndef multiply(a, b):\n    return a * b\n",
        "add multiply function",
    )

    out_file = tmp_path / "dataset.jsonl"
    stats = build_dataset(
        repo_path=str(repo),
        out_path=str(out_file),
        max_diff_lines=400,
        min_age_days=0,  # 0 for test fixture
    )

    assert stats.buggy_count == 1
    assert stats.clean_count >= 1
    assert stats.skipped_count == 0

    # Read back identically
    cases = read_dataset(str(out_file))
    assert len(cases) == stats.buggy_count + stats.clean_count

    # Check buggy case
    buggy_cases = [c for c in cases if c.label == "buggy"]
    assert len(buggy_cases) == 1
    b_case = buggy_cases[0]
    assert b_case.commit_sha == sha_b
    assert b_case.fix_sha == sha_c
    assert len(b_case.buggy_locations) == 1
    assert b_case.buggy_locations[0]["introducing_sha"] == sha_b
    assert b_case.buggy_locations[0]["file"] == "calc.py"
    assert "return a * b  # BUG" in b_case.diff

    # Check clean case
    clean_cases = [c for c in cases if c.label == "clean"]
    assert any(c.commit_sha == sha_d for c in clean_cases)
    for c_case in clean_cases:
        assert c_case.fix_sha is None
        assert c_case.buggy_locations == []


def test_oversized_diff_skipped(tmp_path: Path) -> None:
    """Commits exceeding max_diff_lines are skipped and counted."""
    repo = _init_repo(tmp_path)
    _commit_file(repo, "data.py", "# initial\n", "initial commit")

    # Generate commit with 50 lines of diff
    large_content = "\n".join(f"line_{i} = {i}" for i in range(50)) + "\n"
    _commit_file(repo, "data.py", large_content, "large commit")

    out_file = tmp_path / "dataset_skip.jsonl"
    stats = build_dataset(
        repo_path=str(repo),
        out_path=str(out_file),
        max_diff_lines=20,  # Cap is 20 lines, commit diff is ~50 lines
        min_age_days=0,
    )

    assert stats.skipped_count >= 1


def test_validate_case_rejects_invalid() -> None:
    """Validation rejects ill-formed cases with ValueError."""
    # Invalid label
    with pytest.raises(ValueError, match="Invalid label"):
        validate_case(
            Case(
                id="test1",
                repo="my_repo",
                commit_sha="a" * 40,
                parent_sha="b" * 40,
                label="unknown",  # type: ignore[arg-type]
                fix_sha=None,
                buggy_locations=[],
                diff="some diff",
            )
        )

    # Buggy case missing fix_sha
    with pytest.raises(ValueError, match="Buggy case must have a fix_sha"):
        validate_case(
            Case(
                id="test2",
                repo="my_repo",
                commit_sha="a" * 40,
                parent_sha="b" * 40,
                label="buggy",
                fix_sha=None,
                buggy_locations=[{"file": "x.py", "introducing_sha": "a" * 40, "start_line": 1, "end_line": 1}],
                diff="some diff",
            )
        )

    # Clean case with fix_sha
    with pytest.raises(ValueError, match="Clean case must not have fix_sha"):
        validate_case(
            Case(
                id="test3",
                repo="my_repo",
                commit_sha="a" * 40,
                parent_sha="b" * 40,
                label="clean",
                fix_sha="c" * 40,
                buggy_locations=[],
                diff="some diff",
            )
        )


def test_cli_dataset_build_command(tmp_path: Path) -> None:
    """Test running devreview dataset build via CLI."""
    repo = _init_repo(tmp_path)
    _commit_file(repo, "file.py", "x = 1\n", "initial commit")
    _commit_file(repo, "file.py", "x = 1\ny = 2\n", "add y")

    out_file = tmp_path / "cli_out.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "devreview",
            "dataset",
            "build",
            str(repo),
            "--out",
            str(out_file),
            "--max-diff-lines",
            "400",
            "--min-age-days",
            "0",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Must print counts of buggy, clean and skipped
    output = result.stdout.lower()
    assert "buggy" in output
    assert "clean" in output
    assert "skipped" in output
    assert out_file.exists()
