"""Build golden datasets from git history and validate cases."""

from __future__ import annotations

import json
import re
import subprocess  # nosec: B404  # required by spec; no git library allowed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

from devreview.dataset.git_history import find_fix_commits
from devreview.dataset.szz import BuggyLocation, find_introducing_commits

# Common source code file extensions
_CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".java",
    ".rb",
    ".php",
    ".cs",
    ".sh",
    ".swift",
    ".kt",
    ".scala",
}


@dataclass(frozen=True)
class Case:
    """A single evaluation case (commit) in the golden dataset."""

    id: str
    repo: str
    commit_sha: str
    parent_sha: str
    label: Literal["buggy", "clean"]
    fix_sha: str | None
    buggy_locations: list[dict[str, Any]]
    diff: str

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Case:
        return cls(
            id=data["id"],
            repo=data["repo"],
            commit_sha=data["commit_sha"],
            parent_sha=data["parent_sha"],
            label=data["label"],
            fix_sha=data.get("fix_sha"),
            buggy_locations=data.get("buggy_locations", []),
            diff=data["diff"],
        )


@dataclass(frozen=True)
class BuildStats:
    """Counts recorded during a dataset build."""

    buggy_count: int
    clean_count: int
    skipped_count: int
    out_path: str


def validate_case(case: Case, max_diff_lines: int | None = None) -> None:
    """Validate a case against the schema invariants.

    Raises
    ------
    ValueError
        If any invariant is violated.
    """
    if not case.id or not isinstance(case.id, str):
        raise ValueError(f"Invalid case id: {case.id!r}")
    if not case.repo or not isinstance(case.repo, str):
        raise ValueError(f"Invalid repo name: {case.repo!r}")
    if not re.match(r"^[0-9a-fA-F]{40}$", case.commit_sha):
        raise ValueError(f"Invalid commit_sha: {case.commit_sha!r}")
    if not re.match(r"^[0-9a-fA-F]{40}$", case.parent_sha):
        raise ValueError(f"Invalid parent_sha: {case.parent_sha!r}")

    if case.label not in ("buggy", "clean"):
        raise ValueError(f"Invalid label: {case.label!r}. Must be 'buggy' or 'clean'.")

    if case.label == "buggy":
        if not case.fix_sha or not isinstance(case.fix_sha, str):
            raise ValueError("Buggy case must have a fix_sha string.")
        if not case.buggy_locations or not isinstance(case.buggy_locations, list):
            raise ValueError("Buggy case must have at least one buggy_location.")
        for loc in case.buggy_locations:
            if not isinstance(loc, dict):
                raise ValueError(f"Buggy location must be a dict: {loc!r}")
            for key in ("introducing_sha", "file", "start_line", "end_line"):
                if key not in loc:
                    raise ValueError(f"Buggy location missing required key '{key}': {loc!r}")
            if loc["start_line"] > loc["end_line"]:
                raise ValueError(f"start_line cannot exceed end_line: {loc!r}")
    else:  # clean
        if case.fix_sha is not None:
            raise ValueError(f"Clean case must not have fix_sha, got: {case.fix_sha!r}")
        if case.buggy_locations:
            raise ValueError(f"Clean case must have empty buggy_locations, got: {case.buggy_locations!r}")

    if not isinstance(case.diff, str) or not case.diff:
        raise ValueError("Diff must be a non-empty string.")

    if max_diff_lines is not None:
        lines = len(case.diff.splitlines())
        if lines > max_diff_lines:
            raise ValueError(f"Diff lines ({lines}) exceed maximum allowed ({max_diff_lines}).")


def _run_git(repo_path: str, args: list[str]) -> str:
    result = subprocess.run(  # nosec: B603, B607  # fixed args, no user input
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _touches_code_files(repo_path: str, parent_sha: str, commit_sha: str) -> bool:
    """Check if the diff between parent and commit touches source code files."""
    changed_files = _run_git(
        repo_path,
        ["diff", "--name-only", parent_sha, commit_sha],
    ).splitlines()

    for file_path in changed_files:
        ext = Path(file_path).suffix.lower()
        if ext in _CODE_EXTENSIONS:
            return True
    return False


def build_dataset(
    repo_path: str,
    out_path: str,
    max_diff_lines: int = 400,
    min_age_days: int = 90,
) -> BuildStats:
    """Build a golden dataset from a git repository and write it to JSONL.

    Parameters
    ----------
    repo_path:
        Path to local git repository.
    out_path:
        Output file path for the .jsonl dataset.
    max_diff_lines:
        Maximum allowed lines of unified diff for a case; larger commits are skipped.
    min_age_days:
        Minimum age in days for clean cases (relative to newest commit). Default 90.

    Returns
    -------
    BuildStats
        Counts of buggy, clean, and skipped cases.
    """
    repo = Path(repo_path).resolve()
    repo_name = repo.name

    # 1. Identify fix commits and map introducing commits to their locations
    fix_shas = find_fix_commits(str(repo))
    introducing_map: dict[str, tuple[str, list[BuggyLocation]]] = {}

    for fix_sha in fix_shas:
        locs = find_introducing_commits(str(repo), fix_sha)
        for loc in locs:
            if loc.introducing_sha not in introducing_map:
                introducing_map[loc.introducing_sha] = (fix_sha, [])
            introducing_map[loc.introducing_sha][1].append(loc)

    # 2. Query all non-merge commits with single parent and timestamp
    log_output = _run_git(
        str(repo),
        ["log", "--no-merges", "--format=%H<SEP>%P<SEP>%ct"],
    ).strip()

    commits: list[tuple[str, str, int]] = []
    newest_ts = 0

    for line in log_output.splitlines():
        if not line:
            continue
        parts = line.split("<SEP>")
        if len(parts) != 3:
            continue
        c_sha, parents, ts_str = parts
        parent_list = parents.strip().split()
        if len(parent_list) != 1:
            # Skip root commits or any unexpected multi-parents
            continue
        ts = int(ts_str)
        if ts > newest_ts:
            newest_ts = ts
        commits.append((c_sha, parent_list[0], ts))

    age_cutoff_ts = newest_ts - (min_age_days * 86400)

    buggy_count = 0
    clean_count = 0
    skipped_count = 0

    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with out_file.open("w", encoding="utf-8") as f:
        for c_sha, p_sha, ts in commits:
            diff_text = _run_git(str(repo), ["diff", "-U3", p_sha, c_sha])
            if not diff_text.strip():
                continue

            diff_line_count = len(diff_text.splitlines())
            if diff_line_count > max_diff_lines:
                skipped_count += 1
                continue

            case_id = f"{repo_name}_{c_sha[:10]}"

            if c_sha in introducing_map:
                fix_sha, locs = introducing_map[c_sha]
                case = Case(
                    id=case_id,
                    repo=repo_name,
                    commit_sha=c_sha,
                    parent_sha=p_sha,
                    label="buggy",
                    fix_sha=fix_sha,
                    buggy_locations=[loc.to_dict() for loc in locs],
                    diff=diff_text,
                )
                validate_case(case, max_diff_lines)
                f.write(json.dumps(case.to_dict()) + "\n")
                buggy_count += 1
            else:
                # Clean candidate: older than cutoff and touches code files
                if ts <= age_cutoff_ts and _touches_code_files(str(repo), p_sha, c_sha):
                    case = Case(
                        id=case_id,
                        repo=repo_name,
                        commit_sha=c_sha,
                        parent_sha=p_sha,
                        label="clean",
                        fix_sha=None,
                        buggy_locations=[],
                        diff=diff_text,
                    )
                    validate_case(case, max_diff_lines)
                    f.write(json.dumps(case.to_dict()) + "\n")
                    clean_count += 1

    return BuildStats(
        buggy_count=buggy_count,
        clean_count=clean_count,
        skipped_count=skipped_count,
        out_path=str(out_file),
    )


def read_dataset(file_path: str) -> list[Case]:
    """Read cases from a JSONL dataset file."""
    cases: list[Case] = []
    with Path(file_path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(Case.from_dict(json.loads(line)))
    return cases
