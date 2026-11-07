# Phase 4 - MVP release

**MVP definition:** a stranger can clone the repo, run `devreview backtest` on their own repository, get an honest report of recall, false alarms and cost per bug caught, and the repo itself blocks regressions.

### T-401 - Markdown report generator
**Do:** `devreview report <run.json> --out report.md`: headline numbers with raw counts, label-noise rate (from `docs/DATASET_AUDIT.md`), 5 real catches, 5 misses, 5 false alarms, cost, model, date, and a "How to read this" section.
**Done when:** a test generates a report from a fixture run and checks every section exists.

### T-402 - Run on two public repos and commit the results
**Do:** build datasets and baselines for two public repos the human approves (different languages if possible). Commit reports to `docs/results/` with repo URL, commit hash and license.
**Don't:** cherry-pick repos or cases for good numbers.
**Done when:** two reports committed; each states its sample size and noise rate.

### T-403 - README with honest results and limits
**Do:** update `README.md`: results table from T-402, a 2-minute quickstart, and a "Limits" section: label noise, "clean" is not "bug-free", small samples, one model tested, location matching tolerance.
**Done when:** every number in the README can be traced to a committed report.

### T-404 - Clean-clone check and tag v0.1.0 (HUMAN)
**Human does:** clone fresh into a new folder, follow only the README quickstart, run `make verify` and one real backtest with a small cap. If it fails, write what confused you in `docs/QUESTIONS.md` and the agent fixes the docs. Then tag `v0.1.0`.

### T-405 - Learning proof review and explainer (HUMAN)
**Human does:** fill the proof table in `docs/LEARNING.md` with real evidence for each MVP skill, then record a 3-minute explanation of DevReview with no notes. Whatever you cannot explain becomes a re-learn list.

## MVP exit gate
All of Phases 0-4 DONE, clean-clone test passed, proof table filled. Next: `docs/MVP_TO_PRODUCT.md`.
