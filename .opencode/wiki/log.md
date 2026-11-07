---
title: Wiki log
tags: [log]
sourceRefs: []
lastReviewed: 2026-11-07
---

# Log

## [2026-11-07] ingest | verify pipeline and Windows toolchain
Created `concepts/verify-pipeline.md` and `concepts/windows-toolchain.md` while completing T-001. Reason: the `add_quirk` tool could not reach its embedding backend (`ECONNREFUSED 127.0.0.1:11434`, no Ollama installed), so these lessons are stored here instead. Sources: `Makefile`, `pyproject.toml`, `scripts/guard.py`, `docs/explanations/T-001.md`, `docs/QUESTIONS.md`.

## [2026-11-07] update | T-002 completed
Installed git hooks via `make setup`. Recorded in `concepts/windows-toolchain.md` that `make` now exists (copy of `mingw32-make`, human decision b) and added section 3b: git hooks fail with `Executable 'ruff' not found` unless `.venv\Scripts` is on PATH, so every commit/push command must set PATH first. Updated `concepts/verify-pipeline.md` context unchanged.

## [2026-11-07] ingest | T-003 local gate proof
Created `concepts/gates.md`: local hook vs server gate, plus the proven block messages from the six T-003 experiments and the key fact that the pre-push hook inspects the working tree (tracked + untracked files), not the commit. Sources: `scripts/guard.py`, `.pre-commit-config.yaml`, `docs/explanations/T-003.md`.

## [2026-11-07] ingest | CI on pull requests
Created `concepts/ci.md`: the two CI jobs, why the probe test had to be CI-only, red/green run links, and three gotchas (green gitleaks is not proof, red checks do not block merges before T-005, and the update-branch merge that reverted T-003 to TODO on main). Sources: `.github/workflows/ci.yml`, `docs/explanations/T-004.md`, job logs from runs 42365004887 and 42365069007.
