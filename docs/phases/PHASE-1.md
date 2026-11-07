# Phase 1 - Ground truth from git history

**Goal (plain English):** build the answer key. To grade a code reviewer you need code changes where you KNOW a bug existed. Git history tells us: if a later commit fixed a bug, the commit that introduced it is a "buggy change". Commits never linked to a fix are "clean" (see limits below).
**Learning outcomes:** golden dataset, ground truth, noisy labels, how `git blame` and diffs work, why evals start with data, not prompts.
**Not in this phase:** any LLM call.

**Fixed definitions (do not change without the human):**
- *Fix commit:* non-merge commit whose subject matches the regex `(?i)\b(fix(es|ed)?|bug|hotfix)\b`. Revert commits are excluded.
- *Introducing commit (simplified SZZ):* for a fix commit F with parent P, take the lines F removed or changed, run `git blame` at P on exactly those lines, and collect the commits that last touched them.
- *Buggy case:* an introducing commit. *Clean case:* a non-merge commit that is not an introducing commit, touches code files, is at least 90 days older than the newest commit, and passes the diff-size limit.
- *Limit to document honestly:* "clean" means "no known later fix", NOT "no bug". A reviewer flag on a clean case may be a real unfixed bug.

### T-101 - CLI skeleton
**Do:** `src/devreview/cli.py` using only the standard library `argparse`: `devreview --version` prints `devreview 0.0.0`; subcommand groups `dataset` and `backtest` exist and print help. Add `[project.scripts] devreview = "devreview.cli:main"` to `pyproject.toml`; re-run `python -m pip install -e ".[dev]"`.
**Done when:** `devreview --version` prints `devreview 0.0.0`; `devreview dataset --help` exits 0; tests cover both.
**Teach:** what a CLI is (like an npm script), argparse, entry points.

### T-102 - Find bug-fix commits
**Do:** `find_fix_commits(repo_path) -> list[str]` in `src/devreview/dataset/git_history.py`, using `subprocess` to call `git`. Tests build a tiny throwaway git repo in `tmp_path` (set `user.name` and `user.email` locally) with known fix and non-fix commits.
**Don't:** hit the network; use a git library (not on the allowlist).
**Done when:** tests pass, including: merge commits excluded, and a commit saying "prefix" or "suffix" does NOT match.
**Teach:** how git stores history; why a keyword heuristic is only a guess.

### T-103 - Find bug-introducing commits (simplified SZZ)
**Do:** `find_introducing_commits(repo_path, fix_sha) -> list[BuggyLocation]` where `BuggyLocation` = `{introducing_sha, file, start_line, end_line}`. Use `git diff -U0 <fix>^ <fix>` to get removed lines and `git blame --porcelain -w -L start,end <fix>^ -- file`. Check `git blame --help` first; the porcelain header's second number is the line number inside the introducing commit, which is what we store. Test with a fixture repo: commit B plants a bug, commit C fixes it, result must point to B and the right lines.
**Done when:** the fixture test passes, plus one test where a whitespace-only commit sits between B and C and is correctly skipped.
**Teach:** SZZ in plain words; why it is approximate (a refactor can "own" the line instead of the real bug source).

### T-104 - Build the golden dataset file
**Do:** `devreview dataset build <repo> --out datasets/<name>.jsonl --max-diff-lines 400`. Each line is JSON: `{id, repo, commit_sha, parent_sha, label: "buggy"|"clean", fix_sha|null, buggy_locations: [..], diff}`. Document the schema in `docs/schemas/case.md`. Validate every case on write (plain Python checks; no new dependency). Skip diffs over the line limit and record how many were skipped.
**Done when:** a test builds a dataset from a fixture repo and reads it back identically; build prints counts of buggy, clean and skipped.
**Teach:** JSONL, golden dataset, why the size cap exists (cost).

### T-105 - Build a dataset from a real public repo
**Do:** the human picks the repo (one main language, 300+ commits, cloned locally) and gives the path. Run the build; write `datasets/README.md` with repo URL, commit hash, license and counts.
**Done when:** the dataset has at least 30 buggy and 60 clean cases, or the agent reports exactly why not.
**Teach:** what the numbers say about how rare real bugs are.

### T-106 - Audit label noise on 50 cases (HUMAN)
**Agent builds first:** `devreview dataset audit <file> --sample 50 --seed 1` shows each case's diff and the fix diff, records the human's y / n / skip, and writes the noise rate to `docs/DATASET_AUDIT.md`.
**Human does:** answer 50 cases honestly.
**Done when:** `docs/DATASET_AUDIT.md` states "X of Y sampled buggy cases were really bug-introducing (noise rate Z%)".
**Teach:** noisy labels: every future score must be read with this error bar in mind.

## Phase 1 exit gate (human)
Dataset committed; noise rate known; you can explain in two minutes how the answer key was made and where it can be wrong.
