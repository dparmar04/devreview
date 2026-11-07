# Phase 2 - Baseline reviewer and scorer

**Goal (plain English):** build the simplest possible AI reviewer, plus the grader that scores it against the answer key. The first score is your baseline: every later improvement must beat this number.
**Learning outcomes:** calling an LLM from code, structured output, tokens and cost, how to define "caught a bug" precisely, recall vs false alarms.
**Rule:** keep the reviewer dumb on purpose (one prompt, one call per case). Cleverness comes later and is measured against this.

**Fixed metric definitions (write them to `docs/METRICS.md` in T-204; do not change without the human):**
- *Finding:* `{file, line, severity, message}` produced by the reviewer for one case.
- *Match:* a finding matches a buggy location if the file is the same and `start_line - 3 <= line <= end_line + 3` (tolerance is configurable, default 3).
- *Buggy case caught* = at least one finding matches. **Recall** = caught buggy cases / buggy cases.
- *Clean case flagged* = at least one finding on a clean case. **False-alarm rate** = flagged clean cases / clean cases.
- **Finding precision** = matched findings / all findings.
- **Cost per bug caught** = total spend / caught buggy cases.
- Always print the raw counts next to every percentage.

### T-201 - LLM client wrapper with a fake for tests
**Do:** the human chooses the provider and adds its SDK to `docs/ALLOWED_DEPS.txt` first. Create `src/devreview/llm.py` with one function `complete(prompt, system) -> LLMResult(text, input_tokens, output_tokens)` and a `FakeLLM` class returning scripted answers. Read the key from an environment variable. Respect provider rate limits: on a 429 response wait and retry with backoff (max 3 tries), and never fire requests in parallel on a free tier. Create `config/models.json` with `provider`, `model_id`, `input_price_per_mtok`, `output_price_per_mtok`, `source_url`, `checked_on`, copied from the provider's official docs and pricing page.
**Don't:** hard-code a model ID or price from memory; put a key in any file; call the network in unit tests.
**Done when:** unit tests pass using `FakeLLM`; one `@pytest.mark.live` test exists and is excluded from `make verify` (show `python -m pytest -m live --collect-only`).
**Teach:** what an API call is, tokens, why tests must never spend money.

### T-202 - Findings schema and strict parsing
**Do:** `review_diff(diff, llm) -> list[Finding]`. The prompt asks for JSON only. Parse strictly; on invalid output retry up to 2 times, then raise a clear error (never return made-up findings). Wrap the diff in clear delimiters and tell the model the diff is data, never instructions.
**Done when:** tests cover valid JSON, garbage output, JSON inside markdown fences, and a diff containing "ignore previous instructions" (the prompt's data/instruction separation is asserted).
**Teach:** why LLM output must be validated like user input; what prompt injection is.

### T-203 - Scorer: match findings to ground truth
**Do:** `score_case(case, findings) -> CaseResult` implementing the fixed definitions above. Hand-write at least 8 test cases with expected results worked out on paper (exact line, within tolerance, just outside, wrong file, no findings on buggy, findings on clean, multiple locations, multiple findings).
**Done when:** all 8 pass and each test's docstring shows the paper calculation.
**Teach:** true/false positives and negatives with a smoke-alarm analogy.

### T-204 - Metrics and saved run results
**Do:** `compute_metrics(results)` and `save_run(...)` writing `runs/<timestamp>.json` (git-ignored) containing config, model, counts, metrics, per-case results and token totals. Write `docs/METRICS.md` with the fixed definitions verbatim.
**Done when:** a test with known counts produces exactly the expected metrics; cost is computed from `config/models.json`.
**Teach:** why you save every run (you cannot compare what you did not record).

### T-205 - End-to-end backtest and first baseline
**Do:** `devreview backtest <dataset> --max-cost-usd N --limit K`. `--max-cost-usd` AND `--max-tokens` are both REQUIRED (free tiers limit tokens, not dollars); the run stops cleanly when either cap is reached and says so. Run on a sample of at most 30 cases first, then the full set only if the human approves the projected cost (print an estimate before spending).
**Don't:** run without a cap; retry endlessly; tune the prompt to the sample.
**Done when:** `docs/BASELINE.md` records dataset, model, date, counts, recall, false-alarm rate, cost per bug caught, and 3 examples of misses.
**Teach:** read the baseline honestly: what is the error bar with so few cases?

## Phase 2 exit gate (human)
A real baseline number exists, produced by a run you can repeat; you can explain recall vs false alarms using your own repo as the example.
