---
title: Local gate vs server gate
tags: [quality, gates, git-hooks, ci, security]
sourceRefs: [.pre-commit-config.yaml, scripts/guard.py, .github/workflows/ci.yml, docs/GUARDRAILS.md, docs/explanations/T-003.md]
lastReviewed: 2026-11-07
---

# Local gate vs server gate

Two different gates, and neither replaces the other.

| | Local gate | Server gate |
|---|---|---|
| Lives in | `.git/hooks/` (pre-commit, pre-push) | GitHub Actions + branch protection |
| Runs | `make verify` on this machine | `verify` and `secrets` jobs on a clean runner |
| Stops | accidents, forgetfulness, half-finished tasks | determined bypasses, `--no-verify`, direct pushes |
| Can be skipped? | yes, `git push --no-verify` | no |

## What the local gate actually inspects

The pre-push hook runs `make verify`, which reads the **working tree**, not the commit being pushed:

- `ruff check .` scans every `.py` file on disk
- `pytest` collects every test file on disk
- guard scans `git ls-files --cached --others --exclude-standard` — tracked **and** untracked-not-ignored files

Consequence, proven in T-003: an uncommitted bad file still blocks the push, even though git would never have sent that file.

## Proven blocks (T-003 evidence)
Six deliberate bad states each blocked a push to a local bare remote:

1. failing test → `make ... [Makefile:15: test] Error 1`
2. lint error → `Remove unused import: os`
3. fake AWS key → `[secret] ... looks like a AWS access key id`
4. task left `IN_PROGRESS` → `[start-to-finish]`
5. `DONE` without explanation → `[explanation-missing]`
6. unapproved dependency → `[dependency-not-allowed]`

## Why the server gate exists
`git push --no-verify` bypasses local hooks entirely. A local hook is a turnstile for honest people; the server gate is what makes the guarantee real. See [[concepts/verify-pipeline]] and [[concepts/windows-toolchain]].
