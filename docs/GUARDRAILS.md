# Guardrails: how bad work gets blocked, and how you catch hallucination

## Part 1 - The three layers
| Layer | Runs when | Checks | Can the agent skip it? |
|---|---|---|---|
| 1. pre-commit | `git commit` | style, formatting, secret scan | Yes (`--no-verify`) |
| 2. pre-push | `git push` | `make verify`: lint, tests, bandit, pip-audit, guard | Yes (`--no-verify`) |
| 3. CI + branch protection | pull request / merge | same checks on a clean machine, commit-message rule, gitleaks | **No** for pushing; see known gap in Part 2 |

**Be honest about this:** layers 1-2 live on the machine where the agent works, so they can be bypassed. Layer 3 is the real lock. Without Part 2, "I can't push unverified work" is not true.

## What `scripts/guard.py` enforces
`start-to-finish` (nothing IN_PROGRESS at push), `one-task-at-a-time`, `invented-task` and `missing-task` (ledger must match the phase files), `explanation-missing/incomplete/too-thin` (DONE needs a full explanation), `dependency-not-allowed` (allowlist), `stub` (no TODO/NotImplementedError in `src/`), `secret` (key patterns), `commit-message` (task ID prefix, CI only).

## Part 2 - GitHub setup (human, once; task T-005)
Use ONE GitHub account (yours). A second "agent account" does not work well here: GitHub's docs list contributing as an outside collaborator as a gap for fine-grained tokens, so the repo-scoped token below would not work for it.
1. Make the repo **public** (fits an open-source portfolio). Branch protection on private repos may need a paid plan: check GitHub's current docs.
2. **Create a repo-scoped token for the agent.** GitHub, profile photo, Settings, Developer settings, Personal access tokens, Fine-grained tokens, Generate new token. Name: `devreview-agent`. Expiration: 30 days. Resource owner: your account. Repository access: **Only select repositories**, then pick `devreview`. Repository permissions: **Contents: Read and write**, **Pull requests: Read and write** (Metadata read is added automatically). Leave every other permission empty, especially Administration. Copy the token once; keep it in a password manager or an environment variable. Never put it in the repo.
3. Settings, Branches (or Rules, Rulesets): protect `main`: require a pull request (0 approvals, so you can merge your own PRs); require status checks `verify` and `secrets` (they appear after the first CI run); block force pushes; include administrators; require branches to be up to date. Do NOT tick "require review from Code Owners" (you cannot approve your own PR).
4. Replace `YOUR_GITHUB_USERNAME` in `.github/CODEOWNERS`. It auto-requests your review on protected files. In this simple setup it is a prompt, not a lock: **before merging, open "Files changed" and check whether any protected file (AGENTS.md section 4) was touched.**
5. **Prove it (T-005):** (a) a direct push to `main` with the agent token is rejected; (b) a PR with a failing test cannot be merged; (c) the agent token cannot open repository Settings or change branch protection.
6. **Known gap:** the token can call the merge API once checks are green. AGENTS.md forbids merging; you merge. A hard stop later means moving the repo into a free GitHub organization with a separate agent account as a member and requiring one approval.

Verified on 2026-11-07

## Part 3 - Catching hallucination yourself (2 minutes per task)
1. Ask: **"Show me the command and its real output."** Tests that were not run are the most common lie.
2. Ask: **"What did you NOT verify?"** A good agent lists things. "Nothing" is a red flag.
3. Ask: **"Which file and line does that?"** Then open it.
4. Run the "How to see it working" command yourself.
5. Spot-check a library call: search the official docs for the function name. If it does not exist, the agent made it up.
6. Weekly: fresh clone, follow only the README, run `make verify`.
When you catch one: tell the agent exactly what was invented, make it log the cause in `docs/LEARNING.md` Failures log, and have it add a test that would have caught it.

## Limits of the guard
It checks structure (tasks, files, dependencies, stubs, keys), not truth. It cannot know if an explanation is correct. That is what Part 3 and the check questions are for.
