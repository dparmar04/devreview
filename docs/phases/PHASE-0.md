# Phase 0 - Foundations and guardrails

**Goal (plain English):** build the seatbelts before the car. After this phase, broken, unsafe or half-finished work cannot be pushed.
**Why first:** with an AI agent writing the code, the process is your quality control.
**Learning outcomes:** what a test, linter, security scan, git hook and CI are; why a green check beats "trust me".
**Do not build any DevReview feature in this phase.**

### T-001 - Environment, package skeleton, smoke test
**Do:** `python -m venv .venv`, activate it, create `src/devreview/__init__.py` containing only `__version__ = "0.0.0"`, create `tests/test_smoke.py` asserting that value, then `python -m pip install -e ".[dev]"`.
**Don't:** add any other code or dependency.
**Done when:** `python -m pytest` passes; `python -c "import devreview; print(devreview.__version__)"` prints `0.0.0`.
**Teach:** virtual environment, package, what a test is.

### T-002 - Make `make verify` green
**Do:** run `make setup` (upgrades pip, installs tools, installs git hooks), then `make verify`. Fix only what fails and is in scope. Needs internet (pip-audit).
**Don't:** edit protected files, skip a check, or add `# noqa`.
**Done when:** `make verify` ends with `GUARD OK` and `ALL CHECKS PASSED`.
**Teach:** ruff (style checker), pytest (test runner), bandit (scans your code for risky patterns), pip-audit (checks libraries for known vulnerabilities), guard (this repo's own rules).

### T-003 - Prove the local gate blocks bad pushes
**Do:** `git init --bare /tmp/devreview-remote.git` and add it as a remote named `sandbox`. On a throwaway branch, try each bad action, run `git push sandbox HEAD`, and confirm it is BLOCKED: (a) a failing test, (b) a lint error, (c) a fake secret: the AWS documentation example key, built in a text file as `"AKIA" + "IOSFODNN7EXAMPLE"` joined, (d) a task left IN_PROGRESS, (e) a task marked DONE with no explanation file, (f) a dependency in `pyproject.toml` that is not in `docs/ALLOWED_DEPS.txt`. Then undo every experiment.
**Don't:** use `--no-verify`; leave any experiment behind.
**Done when:** the explanation's Evidence shows the real "blocked" output for all six, and `git status` is clean afterwards.
**Teach:** git hook, why blocking beats reminding, why local hooks can be skipped (see `docs/GUARDRAILS.md`).

### T-004 - CI runs on pull requests
**Do:** with the human's repo on GitHub, open a PR containing one deliberately failing test and confirm both CI jobs (`verify`, `secrets`) run and `verify` goes red; fix it and confirm green. Check the versions of `actions/checkout`, `actions/setup-python` and `gitleaks/gitleaks-action` used in `.github/workflows/ci.yml` against their official pages and report whether they are current. Do not edit the workflow: propose any change in QUESTIONS.md.
**Done when:** links to one red run and one green run are in the Evidence.
**Teach:** CI (a robot that re-runs all checks on a clean machine), why "works on my machine" is not proof.

### T-005 - Turn on branch protection (HUMAN)
**Human does:** follow `docs/GUARDRAILS.md` section "GitHub setup", then run the three proofs listed there. Replace `YOUR_GITHUB_USERNAME` in `.github/CODEOWNERS`.
**Done when:** a push to `main` with the agent token is rejected, and a PR with red CI cannot be merged. Write "Verified on <date>" at the bottom of `docs/GUARDRAILS.md`.

## Phase 0 exit gate (human)
All five tasks DONE; `make verify` green from a fresh clone; you can explain each gate in one sentence; `docs/LEARNING.md` updated.
