# DevReview

An open-source AI code reviewer that **proves its own accuracy on your repo** before you trust it.

AI reviewers all claim they find bugs. None let you verify that claim on your own codebase. DevReview does:

1. Walks your git history and finds bugs that were later fixed (the answer key).
2. Re-reviews the original changes blind, with an LLM.
3. Reports bugs caught, false alarms, and **cost per bug caught**.
4. Re-run after any prompt or model change: the regression gate fails if scores drop.

**Status:** see `docs/PROGRESS.md`. Nothing here is built yet beyond the guardrails kit.

## Start here (human)
1. Create a public GitHub repo, clone it, copy this kit into it, commit.
2. Follow `docs/GUARDRAILS.md` Part 2 once (repo-scoped token for the agent, branch protection on `main`).
3. Give your coding agent this first message:

> Read AGENTS.md fully and obey it. Follow "Session start" and begin with the first TODO task in docs/PROGRESS.md. After every task, explain it to me as a beginner using the format in AGENTS.md section 2, ask me the 2 check questions, and wait for my answers before continuing.

## Map
| File | Purpose |
|---|---|
| `AGENTS.md` | Rules for the agent: loop, teaching, anti-hallucination, security |
| `docs/PROGRESS.md` | Task ledger (machine-checked) |
| `docs/phases/PHASE-0..4.md` | Detailed tasks to the MVP, each with "Done when" |
| `docs/ROADMAP.md` | All phases to the product |
| `docs/MVP_TO_PRODUCT.md` | What separates the MVP from a real product |
| `docs/GUARDRAILS.md` | How pushes are blocked; how you catch hallucination |
| `docs/LEARNING.md` | Skill proof table, failures log, glossary |
| `docs/ALLOWED_DEPS.txt` | The only packages allowed (human-edited) |
| `docs/QUESTIONS.md` | Where the agent asks instead of guessing |
| `scripts/guard.py` | The process and anti-hallucination checks |

## Develop
```
python -m venv .venv && source .venv/bin/activate
make setup      # upgrade pip, install tools, install git hooks
make verify     # lint + tests + security + guard (also runs before every push)
```

## Pitch (one breath)
"AI code reviewers all claim accuracy but none let you verify it on your own repo. I built one that backtests itself against your git history, blocks its own regressions, and reports cost per bug caught."
