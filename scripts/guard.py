#!/usr/bin/env python3
"""Process + anti-hallucination guard.

Exit 0 = all good. Exit 1 = something is wrong. Messages are written for an AI coding
agent to read: they say which rule broke and what to do next.

Usage:
  python scripts/guard.py                  all checks (make verify, pre-push, CI)
  python scripts/guard.py --secrets-only   fast secret scan (pre-commit)
  python scripts/guard.py --commits BASE   also check commit messages in BASE..HEAD (CI)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROGRESS = ROOT / "docs" / "PROGRESS.md"
PHASES = ROOT / "docs" / "phases"
EXPLANATIONS = ROOT / "docs" / "explanations"
ALLOWLIST = ROOT / "docs" / "ALLOWED_DEPS.txt"

VALID_STATUS = {"TODO", "IN_PROGRESS", "DONE", "BLOCKED"}
REQUIRED_HEADINGS = [
    "## What it is",
    "## What I built here",
    "## How it works",
    "## How to see it working",
    "## What could go wrong",
    "## Sources I checked",
    "## Evidence",
    "## Check yourself",
]
MIN_EXPLANATION_CHARS = 800
STUB_PATTERNS = [
    (re.compile(r"\bNotImplementedError\b"), "NotImplementedError (unfinished code)"),
    (re.compile(r"\bTODO\b"), "TODO marker (unfinished work)"),
    (re.compile(r"\bFIXME\b"), "FIXME marker (unfinished work)"),
    (re.compile(r"lorem ipsum", re.I), "placeholder text"),
    (re.compile(r"your[_-]?api[_-]?key[_-]?here", re.I), "placeholder credential"),
]
SECRET_PATTERNS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "GitHub personal access token"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{40,}"), "GitHub fine-grained token"),
    (re.compile(r"sk-[A-Za-z0-9_\-]{20,}"), "API key (sk- prefix)"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "Slack token"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"), "private key"),
    (
        re.compile(r"""(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*['"][A-Za-z0-9_\-/+=]{16,}['"]"""),
        "hard-coded credential",
    ),
]
LEDGER_ROW = re.compile(r"^\|\s*(T-\d{3})\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*$")
COMMIT_OK = re.compile(r"^(T-\d{3}: \S.*|Merge .*)$")

Problem = tuple[str, str]  # (rule, message)


def git(*args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"`git {' '.join(args)}` failed: {proc.stderr.strip()}")
    return proc.stdout


def parse_ledger(problems: list[Problem]) -> list[tuple[str, str, str]]:
    """Return [(task_id, title, status)] from docs/PROGRESS.md."""
    if not PROGRESS.exists():
        problems.append(("ledger", "docs/PROGRESS.md is missing. Restore it; do not recreate from memory."))
        return []
    rows = []
    for line in PROGRESS.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| T-"):
            continue
        m = LEDGER_ROW.match(line)
        if not m:
            problems.append(
                ("ledger", f"Malformed task row in PROGRESS.md: {line!r}. Format: | T-001 | phase | title | STATUS |")
            )
            continue
        task_id, _phase, title, status = m.groups()
        if status not in VALID_STATUS:
            problems.append(("ledger", f"{task_id} has invalid status {status!r}. Allowed: {sorted(VALID_STATUS)}."))
        rows.append((task_id, title, status))
    ids = [r[0] for r in rows]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(("ledger", f"{dup} appears more than once in PROGRESS.md."))
    return rows


def check_process(problems: list[Problem]) -> None:
    rows = parse_ledger(problems)
    defined: set[str] = set()
    if PHASES.exists():
        for f in PHASES.glob("*.md"):
            defined |= set(re.findall(r"^###\s+(T-\d{3})\b", f.read_text(encoding="utf-8"), re.M))
    ledger_ids = {r[0] for r in rows}
    for task_id in sorted(ledger_ids - defined):
        problems.append(
            (
                "invented-task",
                f"{task_id} is in PROGRESS.md but defined in no docs/phases/*.md file. Tasks may not be invented: ask the human.",
            )
        )
    for task_id in sorted(defined - ledger_ids):
        problems.append(
            (
                "missing-task",
                f"{task_id} is defined in a phase file but missing from PROGRESS.md. Do not delete tasks from the ledger.",
            )
        )

    unfinished = [r[0] for r in rows if r[2] == "IN_PROGRESS"]
    if len(unfinished) > 1:
        problems.append(
            ("one-task-at-a-time", f"More than one task is IN_PROGRESS: {unfinished}. Only one is allowed.")
        )
    if unfinished:
        problems.append(
            (
                "start-to-finish",
                f"{unfinished} is still IN_PROGRESS. Finish it (status DONE with explanation) before pushing. If you cannot finish, do not push; write why in docs/QUESTIONS.md.",
            )
        )

    for task_id, title, status in rows:
        if status != "DONE" or "(HUMAN)" in title:
            continue
        path = EXPLANATIONS / f"{task_id}.md"
        if not path.exists():
            problems.append(
                (
                    "explanation-missing",
                    f"{task_id} is DONE but docs/explanations/{task_id}.md does not exist. Copy docs/explanations/_TEMPLATE.md and fill it in.",
                )
            )
            continue
        text = path.read_text(encoding="utf-8")
        missing = [h for h in REQUIRED_HEADINGS if not re.search(rf"^{re.escape(h)}\s*$", text, re.M)]
        if missing:
            problems.append(("explanation-incomplete", f"{path.name} is missing sections: {missing}."))
        if "FILL_ME" in text:
            problems.append(("explanation-incomplete", f"{path.name} still contains FILL_ME placeholders."))
        if len(text) < MIN_EXPLANATION_CHARS:
            problems.append(
                (
                    "explanation-too-thin",
                    f"{path.name} is under {MIN_EXPLANATION_CHARS} characters. Explain properly, for a beginner.",
                )
            )


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def requirement_name(req: str) -> str:
    return norm(re.split(r"[\s<>=!~;\[(@]", req.strip(), maxsplit=1)[0])


def check_dependencies(problems: list[Problem]) -> None:
    pyproject = ROOT / "pyproject.toml"
    if not pyproject.exists():
        problems.append(("deps", "pyproject.toml is missing."))
        return
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project = data.get("project", {})
    reqs = list(project.get("dependencies", []))
    for group in project.get("optional-dependencies", {}).values():
        reqs.extend(group)
    for group in data.get("dependency-groups", {}).values():
        reqs.extend(r for r in group if isinstance(r, str))
    allowed = set()
    if ALLOWLIST.exists():
        for line in ALLOWLIST.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                allowed.add(norm(line))
    for req in reqs:
        name = requirement_name(req)
        if name not in allowed:
            problems.append(
                (
                    "dependency-not-allowed",
                    f"Dependency {name!r} is not in docs/ALLOWED_DEPS.txt. Do NOT add it yourself. Package names you invent may not exist or may be malicious. Remove it, or ask the human in docs/QUESTIONS.md.",
                )
            )


def check_stubs(problems: list[Problem]) -> None:
    src = ROOT / "src"
    if not src.exists():
        return
    for path in sorted(src.rglob("*.py")):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pattern, what in STUB_PATTERNS:
                if pattern.search(line):
                    problems.append(
                        ("stub", f"{path.relative_to(ROOT)}:{n}: {what}. Finish the work or do not mark the task DONE.")
                    )


def check_secrets(problems: list[Problem]) -> None:
    try:
        files = git("ls-files", "--cached", "--others", "--exclude-standard").splitlines()
    except RuntimeError as exc:
        problems.append(("secrets", f"Cannot list files: {exc}"))
        return
    for rel in files:
        if rel == "scripts/guard.py":
            continue
        path = ROOT / rel
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for pattern, what in SECRET_PATTERNS:
                if pattern.search(line):
                    problems.append(
                        (
                            "secret",
                            f"{rel}:{n}: looks like a {what}. Remove it, load it from an environment variable, and tell the human: the key may need rotating.",
                        )
                    )


def check_commits(base: str, problems: list[Problem]) -> None:
    try:
        subjects = git("log", f"{base}..HEAD", "--format=%s").splitlines()
    except RuntimeError as exc:
        problems.append(("commits", f"Cannot read commits: {exc}"))
        return
    for subject in subjects:
        if not COMMIT_OK.match(subject):
            problems.append(
                ("commit-message", f"Commit {subject!r} does not start with a task ID. Use: 'T-102: what changed'.")
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--secrets-only", action="store_true")
    parser.add_argument("--commits", metavar="BASE")
    args = parser.parse_args()

    problems: list[Problem] = []
    check_secrets(problems)
    if not args.secrets_only:
        check_process(problems)
        check_dependencies(problems)
        check_stubs(problems)
    if args.commits:
        check_commits(args.commits, problems)

    if problems:
        print("GUARD FAILED. You (the agent) broke a process rule, or you may be hallucinating.")
        print("STOP. Do not work around this. Fix the CAUSE, then tell the human in plain English what went wrong.\n")
        for rule, message in problems:
            print(f"  [{rule}] {message}")
        return 1
    print("GUARD OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
