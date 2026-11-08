---
title: The verify pipeline (lint, test, security, guard)
tags: [quality, gates, make, ci]
sourceRefs: [Makefile, pyproject.toml, scripts/guard.py, tests/test_guard.py, docs/GUARDRAILS.md]
lastReviewed: 2026-11-07
---

# The verify pipeline

`make verify` is the single command that decides whether work may be pushed. It runs four gates in order and prints `ALL CHECKS PASSED` only if all four pass.

| Gate | Command | Catches |
|---|---|---|
| lint | `ruff check .` and `ruff format --check .` | style errors, unused imports, import order, common bug patterns (rules `E,F,I,B`) |
| test | `pytest` | behaviour regressions; `-m 'not live'` excludes paid API tests |
| security | `bandit -r src -q` and `pip-audit` | risky code patterns in `src/`; known CVEs in installed packages |
| guard | `python scripts/guard.py` | process rules: `PROGRESS.md` format, one IN_PROGRESS task, DONE needs an explanation file, no secrets, deps must be in `docs/ALLOWED_DEPS.txt` |

Notes observed in practice:
- `pip-audit` reports `devreview Dependency not found on PyPI and could not be audited` — expected, it is the local package.
- Guard fails while a task is IN_PROGRESS; that is intended, so `verify` is only fully green at the end of a task.
- Protected files (`Makefile`, `scripts/`, `.github/`, `tests/test_guard.py`, `.pre-commit-config.yaml`, `AGENTS.md`, `docs/ALLOWED_DEPS.txt`, `evals/thresholds.json`) may be read but never edited by the agent.

Windows specifics (no `make`, venv on PATH, PowerShell exit codes): see [[concepts/windows-toolchain]].
