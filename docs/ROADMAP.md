# Roadmap

Rule: only the current phase is planned in detail. Later phases get a phase file (same template) when you reach them. The agent must never build ahead.

| Phase | Name | Outcome | Status |
|---|---|---|---|
| 0 | Foundations and guardrails | Bad pushes are blocked | detailed |
| 1 | Ground truth from git history | Golden dataset + known label noise | detailed |
| 2 | Baseline reviewer and scorer | First honest score | detailed |
| 3 | Regression gate + validated judge | Cannot silently get worse | detailed |
| 4 | **MVP release (v0.1.0)** | Anyone can backtest a reviewer on their repo | detailed |
| 5 | Tracing | See every LLM call (inputs, outputs, cost) with a tracing tool such as Langfuse; find one real bug through a trace | outline |
| 6 | GitHub Action | Live PR comments; silent by default: only post findings above a confidence level calibrated from the backtest | outline |
| 7 | Repo context (RAG) | Reviewer reads relevant code first (keyword + meaning search + re-ranking). Proof = backtest score before vs after | outline |
| 8 | Router and cost control | Cheap model first, escalate when unsure. Proof = same recall, lower cost per bug caught | outline |
| 9 | Live scoreboard | Dashboard of accepted / ignored / dismissed comments and precision over time (Next.js, your home turf) | outline |
| 10 | Tools and tuning | MCP server exposing review and backtest as tools; optional small-model fine-tune (LoRA) only if enough accepted-comment data exists | outline |

**Every phase from 5 on follows the same loop:** change one thing, run the backtest, keep it only if the number improves. No number, no merge.

**Phase exit gate (every phase):** all tasks DONE; `make verify` green from a fresh clone; the human can explain the phase in two minutes without notes; `docs/LEARNING.md` updated.
