---
title: Branch protection on main
tags: [github, gates, branch-protection, t-005, incident]
sourceRefs: [docs/GUARDRAILS.md, .github/CODEOWNERS, docs/PROGRESS.md]
lastReviewed: 2026-11-07
---

# Branch protection on `main`

The server-side gate. Without working enforcement, CI is advisory: a red PR still merges.

## Status: **NOT enforced** (proven 2026-11-07)

`main` reports `"protected": true`, but the required status checks are not blocking merges.

Proof (b) was run for real: branch `experiment/t-005-proof` added a test that fails only when `CI=true`, PR #6 showed `verify: failure`, and then:

```
PUT /repos/dparmar04/devreview/pulls/6/merge
→ MERGE SUCCEEDED (unexpected): merged=True sha=5e2931b0e865c4d9bb45959b95e31a916020cbc7
```

Result: a deliberately red test landed on `main`, and CI on `main` went red. Fix PR #7 removes it.

## Likely causes (not yet confirmed — the token cannot read the rules)

`GET /branches/main/protection` returns **403** because the agent token has no `Administration` permission. So the rule's contents are invisible to the agent and must be checked by the human:

1. "Require status checks to pass before merging" is actually ticked.
2. `verify` and `secrets` are selected in the check list (they only appear after a run; the UI may show them as `ci / verify`).
3. Bypass is disabled — "Do not allow bypassing the above settings" / "include administrators". The token acts as the repo **owner**, so if admins may bypass, every agent merge bypasses the gate.
4. The rule targets `main` (branch rule or ruleset), not a pattern that misses it.

## The three proofs

| # | Claim | Result |
|---|---|---|
| a | direct push to `main` with the agent token is rejected | not yet run |
| b | a PR with a failing check cannot be merged | **FAILED** — merged anyway |
| c | the agent token cannot read or change protection | pass (`403` on `/protection`) |

## Verified facts

- `GET /repos/.../branches/main` → `"protected": true`
- `.github/CODEOWNERS` uses `@dparmar04` (placeholder replaced)
- The merge API is callable with Contents + Pull requests write, once checks are green *or bypassed*

## Lesson

`"protected": true` is a label, not a guarantee. A gate is only real when someone has tried to break it and failed. That is exactly why T-005 asks for proofs instead of a settings screenshot.

## Related

[[concepts/gates]] · [[concepts/ci]]
