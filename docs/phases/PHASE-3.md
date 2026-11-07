# Phase 3 - The unique part: regression gate and validated judge

**Goal (plain English):** make DevReview refuse to get worse silently. Change the model or prompt, re-run the backtest, and the gate says pass or fail with numbers. Then make sure any AI "judge" is itself checked against human answers.
**Learning outcomes:** caching and determinism, comparing runs fairly, thresholds, statistical noise, LLM-as-judge and why it must be validated.

### T-301 - Response cache (record and replay)
**Do:** cache LLM responses on disk keyed by a hash of (model_id, prompt, diff). A cache hit costs nothing and returns the identical text. Add `--no-cache`. Cache directory is git-ignored.
**Done when:** a test shows the second run makes zero LLM calls and gives identical results; changing the prompt text invalidates the entry.
**Teach:** caching, hashing, why identical inputs should give identical results in tests.

### T-302 - Compare two runs
**Do:** `devreview compare <run_a.json> <run_b.json>` prints per-metric deltas with raw counts, and lists cases that flipped (caught to missed and the reverse). Both runs must use the same dataset; otherwise exit with an error.
**Done when:** tests cover improved, worse, identical and mismatched-dataset runs.
**Teach:** paired comparison on the same cases is fairer than comparing two averages.

### T-303 - Regression gate with thresholds
**Do:** the human creates `evals/thresholds.json` (protected file): `{"max_recall_drop": 0.03, "max_false_alarm_rise": 0.03, "max_cost_ratio": 1.25, "min_cases_for_gate": 100}`. `devreview gate <candidate_run> <baseline_run>` exits 1 if a limit is exceeded and `min_cases_for_gate` is met; below that case count it prints WARN with the reason and exits 0. Document how to refresh the stored baseline run.
**Don't:** edit the thresholds file; make the gate lenient to pass.
**Done when:** tests cover pass, fail on recall, fail on false alarms, fail on cost, and WARN on a small dataset. `make verify` runs the gate against stored fixture runs only (no paid calls).
**Teach:** why a 3-point drop on 30 cases (1 case) is noise, not proof, and why the gate warns instead of failing there.

### T-304 - LLM judge validated against human labels
**Do:** an optional judge that decides whether an unmatched finding describes the same bug as the fix commit. The human labels 30 (finding, case) pairs in `datasets/judge_labels.jsonl`. `devreview judge-eval` reports agreement % and a confusion table. The judge may only be used in scoring if agreement is at least the target the human sets in `docs/METRICS.md` (suggested: 80%).
**Done when:** agreement is measured and recorded; if it is below target, the judge stays off and the report says so.
**Teach:** LLM-as-judge: a second AI grading the first, and why an unvalidated judge is just a second guess.

## Phase 3 exit gate (human)
You can change the prompt, run one command, and show a pass/fail verdict with numbers. You can explain why the gate sometimes only warns.
