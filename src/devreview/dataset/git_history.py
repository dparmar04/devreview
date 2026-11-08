"""Identify bug-fix commits from git history.

Uses only ``subprocess`` to call git — no third-party git library.
"""

from __future__ import annotations

import re
import subprocess  # nosec: B404  # required by spec; no git library allowed

# Regex from the project spec (PHASE-1.md):
#   non-merge commit whose subject matches (?i)\b(fix(es|ed)?|bug|hotfix)\b
#   revert commits are excluded.
_FIX_RE = re.compile(r"(?i)\b(fix(es|ed)?|bug|hotfix)\b")
_REVERT_RE = re.compile(r"(?i)^revert\b")


def find_fix_commits(repo_path: str) -> list[str]:
    """Return SHAs of non-merge, non-revert commits whose subject matches the fix regex.

    Parameters
    ----------
    repo_path:
        Absolute or relative path to a local git repository.

    Returns
    -------
    list[str]
        Full 40-character SHA hex strings, newest first.
    """
    # --no-merges excludes merge commits.
    # --format gives us "sha<SEP>subject" so we can inspect the subject.
    separator = "<SEP>"
    result = subprocess.run(  # nosec: B603, B607  # fixed args, no user input
        [
            "git",
            "log",
            "--no-merges",
            f"--format=%H{separator}%s",
        ],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )

    fix_shas: list[str] = []
    for line in result.stdout.strip().splitlines():
        if not line:
            continue
        sha, subject = line.split(separator, maxsplit=1)
        if _REVERT_RE.search(subject):
            continue
        if _FIX_RE.search(subject):
            fix_shas.append(sha)

    return fix_shas
