"""Tests for find_fix_commits (T-102).

Each test builds a tiny throwaway git repo inside pytest's tmp_path,
makes commits with known messages, and checks which ones
find_fix_commits returns.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from devreview.dataset.git_history import find_fix_commits

# ── helpers ──────────────────────────────────────────────────────────────────


def _git(repo: Path, *args: str) -> str:
    """Run a git command in *repo* and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    """Create a fresh git repo with local user config and one initial commit."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "user.email", "test@test.com")
    # Initial commit so there is a HEAD
    (repo / "readme.md").write_text("# test repo\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "initial commit")
    return repo


def _commit(repo: Path, message: str, filename: str | None = None) -> str:
    """Create a file, commit it, and return the SHA."""
    if filename is None:
        filename = message.replace(" ", "_") + ".txt"
    (repo / filename).write_text(message + "\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


# ── tests ────────────────────────────────────────────────────────────────────


def test_basic_fix_keywords(tmp_path: Path) -> None:
    """Commits with 'fix', 'fixes', 'fixed', 'bug', 'hotfix' are found."""
    repo = _init_repo(tmp_path)
    sha_fix = _commit(repo, "fix null pointer")
    sha_fixes = _commit(repo, "fixes login crash")
    sha_fixed = _commit(repo, "fixed typo in parser")
    sha_bug = _commit(repo, "bug in validation logic")
    sha_hotfix = _commit(repo, "hotfix: patch auth flow")

    result = find_fix_commits(str(repo))

    assert sha_fix in result
    assert sha_fixes in result
    assert sha_fixed in result
    assert sha_bug in result
    assert sha_hotfix in result


def test_non_fix_commits_excluded(tmp_path: Path) -> None:
    """Normal commits without fix keywords are not returned."""
    repo = _init_repo(tmp_path)
    _commit(repo, "add new feature")
    _commit(repo, "refactor database layer")
    _commit(repo, "update README")

    result = find_fix_commits(str(repo))

    assert result == []


def test_merge_commits_excluded(tmp_path: Path) -> None:
    """Merge commits are excluded even if their message contains a fix keyword."""
    repo = _init_repo(tmp_path)
    # Create a branch, commit there, merge back
    _git(repo, "checkout", "-b", "feature")
    _commit(repo, "fix something on feature", "feature.txt")
    _git(repo, "checkout", "master")
    # Make a divergent commit on master so the merge is not fast-forward
    _commit(repo, "unrelated work on master", "master.txt")
    _git(repo, "merge", "feature", "-m", "Merge branch feature: fix something")

    result = find_fix_commits(str(repo))

    # The non-merge fix commit on the feature branch IS included
    assert len([s for s in result]) >= 1
    # But the merge commit itself is not
    merge_sha = _git(repo, "rev-parse", "HEAD")
    assert merge_sha not in result


def test_revert_commits_excluded(tmp_path: Path) -> None:
    """Revert commits are excluded even if they mention 'fix'."""
    repo = _init_repo(tmp_path)
    _commit(repo, "fix timeout issue")
    _commit(repo, 'Revert "fix timeout issue"', "revert_fix.txt")

    result = find_fix_commits(str(repo))

    # Only the original fix, not the revert
    subjects = []
    for sha in result:
        subj = _git(repo, "log", "--format=%s", "-1", sha)
        subjects.append(subj)
    assert any("fix timeout" in s for s in subjects)
    assert not any("Revert" in s for s in subjects)


def test_prefix_suffix_no_match(tmp_path: Path) -> None:
    r"""Words like 'prefix', 'suffix', 'fixing' where fix is a substring do NOT match.

    The regex uses \\b word boundaries, so 'prefix' should not trigger a match.
    'fixing' also should not match because the regex only allows fix/fixes/fixed.
    """
    repo = _init_repo(tmp_path)
    _commit(repo, "add prefix to identifiers")
    _commit(repo, "handle suffix trimming")
    _commit(repo, "fixing the build process")  # 'fixing' is not fix/fixes/fixed

    result = find_fix_commits(str(repo))

    assert result == []


def test_case_insensitive(tmp_path: Path) -> None:
    """The regex is case-insensitive: 'FIX', 'Bug', 'HOTFIX' all match."""
    repo = _init_repo(tmp_path)
    sha1 = _commit(repo, "FIX: uppercase fix")
    sha2 = _commit(repo, "Bug Report handled")
    sha3 = _commit(repo, "HOTFIX deployed")

    result = find_fix_commits(str(repo))

    assert sha1 in result
    assert sha2 in result
    assert sha3 in result
