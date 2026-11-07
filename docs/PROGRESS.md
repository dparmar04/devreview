# Progress ledger

Format is machine-checked by `scripts/guard.py`. Statuses: TODO, IN_PROGRESS, DONE, BLOCKED.
Only one task may be IN_PROGRESS. Details of every task live in `docs/phases/PHASE-N.md`.
Tasks with (HUMAN) in the title are done and marked by the human.

| ID | Phase | Title | Status |
|----|-------|-------|--------|
| T-001 | 0 | Environment, package skeleton, smoke test | DONE |
| T-002 | 0 | Make `make verify` green | DONE |
| T-003 | 0 | Prove the local gate blocks bad pushes | DONE |
| T-004 | 0 | CI runs on pull requests | DONE |
| T-005 | 0 | Turn on branch protection (HUMAN) | DONE |
| T-101 | 1 | CLI skeleton | DONE |
| T-102 | 1 | Find bug-fix commits | TODO |
| T-103 | 1 | Find bug-introducing commits (simplified SZZ) | TODO |
| T-104 | 1 | Build the golden dataset file | TODO |
| T-105 | 1 | Build a dataset from a real public repo | TODO |
| T-106 | 1 | Audit label noise on 50 cases (HUMAN) | TODO |
| T-201 | 2 | LLM client wrapper with a fake for tests | TODO |
| T-202 | 2 | Findings schema and strict parsing | TODO |
| T-203 | 2 | Scorer: match findings to ground truth | TODO |
| T-204 | 2 | Metrics and saved run results | TODO |
| T-205 | 2 | End-to-end backtest and first baseline | TODO |
| T-301 | 3 | Response cache (record and replay) | TODO |
| T-302 | 3 | Compare two runs | TODO |
| T-303 | 3 | Regression gate with thresholds | TODO |
| T-304 | 3 | LLM judge validated against human labels | TODO |
| T-401 | 4 | Markdown report generator | TODO |
| T-402 | 4 | Run on two public repos, commit results | TODO |
| T-403 | 4 | README with honest results and limits | TODO |
| T-404 | 4 | Clean-clone check and tag v0.1.0 (HUMAN) | TODO |
| T-405 | 4 | Learning proof review and explainer (HUMAN) | TODO |
