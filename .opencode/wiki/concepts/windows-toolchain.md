---
title: Windows toolchain quirks (devreview)
tags: [environment, windows, make, powershell, toolchain]
sourceRefs: [Makefile, docs/explanations/T-001.md, docs/QUESTIONS.md]
lastReviewed: 2026-11-07
---

# Windows toolchain quirks

Facts learned while doing T-001 on this machine. None of these are bugs in the repo; they are environment mismatches between the repo's Linux-ish assumptions and this Windows box.

## 1. `make` was missing; fixed with a copy of `mingw32-make` (2026-11-07)
Originally `make` was not on PATH. `mingw32-make.exe` exists at `C:\msys64\ucrt64\bin\mingw32-make.exe` (also `C:\Strawberry\c\bin`) and is the same GNU Make program under a different file name.

Human decision (option **b**, 2026-11-07): `Copy-Item C:\msys64\ucrt64\bin\mingw32-make.exe C:\msys64\ucrt64\bin\make.exe`. `make --version` now reports `GNU Make 4.4.1`, so plain `make <target>` works, which the installed **pre-push hook** requires (its entry is literally `make verify`). Undo with `Remove-Item C:\msys64\ucrt64\bin\make.exe`.

`Makefile` is a protected file — do not edit it, and do not edit `.pre-commit-config.yaml` either. Record substitutions in each task's explanation file.

Either form works, provided `.venv\Scripts` is on PATH:

```powershell
$env:PATH = "$pwd\.venv\Scripts;$env:PATH"
make verify
```

## 2. The venv must be on PATH, not merely installed
The `lint`, `test` and `security` recipes call bare `ruff`, `pytest`, `bandit`, `pip-audit`. Windows resolves a bare name only through PATH. `.venv\Scripts` is not on PATH until the venv is activated (or prepended manually), so the recipe fails with:

```
process_begin: CreateProcess(NULL, ruff check ., ...) failed.
make (e=2): The system cannot find the file specified.
```

Fixes: `.\.venv\Scripts\Activate.ps1` (per terminal) or the PATH line above. Calling `.\.venv\Scripts\python.exe -m pytest` works too because it names the interpreter directly. Node analogy: this is `node_modules/.bin`, which `npm run` adds for you and Python does not.

## 3. PowerShell 5.1 turns successful stderr into "Exited with code 1"
Piping a native command's stderr (`2>&1 | Select-Object`) makes PowerShell report `NativeCommandError` / exit code 1 even when the command succeeded. `pip install` triggers it via the "new release of pip is available" notice; `git push` triggers it via remote hints.

Judge success from the output text (`Successfully installed`, `GUARD OK`, `ALL CHECKS PASSED`), or capture the exit code without `2>&1`.

## 3b. Git hooks need the venv active, or they block the commit
`pre-commit install` created `.git/hooks/pre-commit` and `.git/hooks/pre-push`. The pre-commit hook runs bare `ruff`; with the venv inactive it fails with `Executable 'ruff' not found` and the commit is refused. The pre-push hook runs bare `make verify`, which needs both `make` and the venv tools.

Practical rule for the agent: every `git commit` / `git push` command must first run `$env:PATH = "$pwd\.venv\Scripts;$env:PATH"` in the same shell invocation, because each shell call is a fresh process with no activation state.

## 4. Guard blocks a push while a task is IN_PROGRESS
`python scripts/guard.py` fails with `['T-XXX'] is still IN_PROGRESS` until the task is `DONE` **and** its explanation file exists. That is the gate working, not a red baseline. `make verify` therefore cannot be fully green mid-task by design.

Related: [[concepts/verify-pipeline]]
