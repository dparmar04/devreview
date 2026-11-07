---
title: CI on pull requests
tags: [ci, github-actions, gates, pytest, security]
sourceRefs: [.github/workflows/ci.yml, Makefile, scripts/guard.py, docs/explanations/T-004.md]
lastReviewed: 2026-11-07
---

# CI on pull requests

GitHub Actions runs the same checks on a **clean machine** (`ubuntu-latest`), which is what makes "works on my machine" falsifiable.

## Jobs (from `.github/workflows/ci.yml`, protected)

| Job | Steps | What it proves |
|---|---|---|
| `verify` | checkout (fetch-depth 0) → setup-python 3.12 → `pip install -e ".[dev]"` → `make verify` → `guard.py --commits origin/<base>` | the full local gate also passes with only declared dependencies; every commit message carries a task ID |
| `secrets` | checkout → `gitleaks/gitleaks-action` | no known secret pattern in the scanned diff |

Triggers: `pull_request` (all default types) and `push` to `main`.

## Why a CI-only failing test was needed

T-004 must show a red run. A test that fails **locally** can never be pushed — the pre-push hook runs `make verify`, pytest fails, git refuses — and `--no-verify` is forbidden. So the probe test asserted on an environment difference instead:

```python
assert os.environ.get("CI") != "true", "deliberate CI-only failure for T-004"
```

`CI` is unset locally, `true` on Actions. Result: `12 passed` locally, `1 failed, 11 passed` in CI, same commit.

## Evidence

- Red: https://github.com/dparmar04/devreview/actions/runs/42365004887 (`verify` failure, `secrets` success)
- Green: https://github.com/dparmar04/devreview/actions/runs/42365069007 (both success)

## Gotchas learned

- **Green `secrets` ≠ no secrets.** gitleaks matches known patterns (provider prefixes, key blocks, entropy). `DB_PASSWORD = "hunter2"` passes it.
- **A red check does not block a merge** until branch protection requires it — that is T-005. See [[concepts/gates]].
- **Deprecated action runtimes**: the red run warned `Node.js 20 is deprecated ... actions/checkout@v4, actions/setup-python@v5` (force-mapped to Node 24). Version proposal lives in `docs/QUESTIONS.md`.
- **A CI-only test must be deleted immediately** after capture, or every later PR is red forever.
- **`git push` does not trigger `pull_request` runs once the PR is closed/merged.** Pushes after merge produce no check suite; open a new PR if a check is needed.
- **The GitHub "Update branch" merge can silently revert ledger lines.** `36df6fd` kept the branch's older `docs/PROGRESS.md` (T-003 `TODO`) over main's newer one, and merging PR #4 propagated that regression to `main`. Always diff `origin/main..HEAD` for `docs/PROGRESS.md` before merging.

## Related

[[concepts/gates]] · [[concepts/verify-pipeline]] · [[concepts/windows-toolchain]]
