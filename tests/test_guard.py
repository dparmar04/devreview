"""Tests for scripts/guard.py. If these fail, the safety net itself is broken: tell the human."""

import shutil
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
EXPLANATION = "# T-001\n\n" + "".join(
    f"{h}\n" + "A plain English paragraph that explains the thing properly. " * 3 + "\n\n"
    for h in [
        "## What it is",
        "## What I built here",
        "## How it works",
        "## How to see it working",
        "## What could go wrong",
        "## Sources I checked",
        "## Evidence",
        "## Check yourself",
    ]
)


def git(path, *args):
    return subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
        cwd=path,
        capture_output=True,
        text=True,
        check=True,
    )


def make_project(tmp_path, status="TODO", deps="", explanation=None, src_code=None, ledger_id="T-001"):
    (tmp_path / "scripts").mkdir()
    shutil.copy(KIT / "scripts" / "guard.py", tmp_path / "scripts" / "guard.py")
    (tmp_path / "docs" / "phases").mkdir(parents=True)
    (tmp_path / "docs" / "explanations").mkdir()
    (tmp_path / "docs" / "ALLOWED_DEPS.txt").write_text("pytest  # test runner\n")
    (tmp_path / "docs" / "phases" / "PHASE-0.md").write_text("### T-001 - First thing\n")
    (tmp_path / "docs" / "PROGRESS.md").write_text(
        f"| ID | Phase | Title | Status |\n|---|---|---|---|\n| {ledger_id} | 0 | First thing | {status} |\n"
    )
    (tmp_path / "pyproject.toml").write_text(f'[project]\nname = "x"\nversion = "0"\ndependencies = [{deps}]\n')
    if explanation is not None:
        (tmp_path / "docs" / "explanations" / "T-001.md").write_text(explanation)
    if src_code is not None:
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "mod.py").write_text(src_code)
    git(tmp_path, "init", "-q")
    return tmp_path


def run_guard(path, *args):
    return subprocess.run([sys.executable, "scripts/guard.py", *args], cwd=path, capture_output=True, text=True)


def test_clean_project_passes(tmp_path):
    result = run_guard(make_project(tmp_path))
    assert result.returncode == 0, result.stdout
    assert "GUARD OK" in result.stdout


def test_in_progress_task_blocks_push(tmp_path):
    result = run_guard(make_project(tmp_path, status="IN_PROGRESS"))
    assert result.returncode == 1
    assert "start-to-finish" in result.stdout


def test_done_without_explanation_fails(tmp_path):
    result = run_guard(make_project(tmp_path, status="DONE"))
    assert result.returncode == 1
    assert "explanation-missing" in result.stdout


def test_done_with_full_explanation_passes(tmp_path):
    result = run_guard(make_project(tmp_path, status="DONE", explanation=EXPLANATION))
    assert result.returncode == 0, result.stdout


def test_explanation_with_placeholder_fails(tmp_path):
    result = run_guard(make_project(tmp_path, status="DONE", explanation=EXPLANATION + "FILL_ME"))
    assert result.returncode == 1
    assert "FILL_ME" in result.stdout


def test_invented_task_fails(tmp_path):
    result = run_guard(make_project(tmp_path, ledger_id="T-999"))
    assert result.returncode == 1
    assert "invented-task" in result.stdout


def test_dependency_not_on_allowlist_fails(tmp_path):
    result = run_guard(make_project(tmp_path, deps='"pytest>=8", "totally-made-up-pkg"'))
    assert result.returncode == 1
    assert "totally-made-up-pkg" in result.stdout


def test_stub_in_src_fails(tmp_path):
    result = run_guard(make_project(tmp_path, src_code="def f():\n    raise NotImplementedError\n"))
    assert result.returncode == 1
    assert "stub" in result.stdout


def test_secret_is_caught_even_in_fast_mode(tmp_path):
    project = make_project(tmp_path)
    (project / "config.txt").write_text("key = " + "AKIA" + "IOSFODNN7EXAMPLE\n")
    result = run_guard(project, "--secrets-only")
    assert result.returncode == 1
    assert "secret" in result.stdout


def test_commit_message_must_start_with_task_id(tmp_path):
    project = make_project(tmp_path)
    git(project, "add", ".")
    git(project, "commit", "-q", "-m", "T-001: base")
    (project / "a.txt").write_text("a")
    git(project, "add", ".")
    git(project, "commit", "-q", "-m", "did some stuff")
    result = run_guard(project, "--commits", "HEAD~1")
    assert result.returncode == 1
    assert "commit-message" in result.stdout
