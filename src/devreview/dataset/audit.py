"""Interactive audit tool to measure label noise in golden datasets (T-106)."""

from __future__ import annotations

import random
import subprocess  # nosec: B404  # required by spec; no git library allowed
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from devreview.dataset.builder import Case, read_dataset


@dataclass(frozen=True)
class AuditStats:
    """Statistics recorded from a manual dataset noise audit."""

    yes_count: int
    no_count: int
    skip_count: int
    total_evaluated: int
    noise_rate: float
    sampled_ids: list[str]
    out_doc: str


def _get_fix_diff(repo_path: str, fix_sha: str) -> str:
    """Fetch the diff or show output of a fix commit from local git repo."""
    try:
        proc = subprocess.run(  # nosec: B603, B607  # fixed args, no user input
            ["git", "show", "--stat", "--patch", "-U3", fix_sha],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        return proc.stdout or ""
    except Exception:
        return ""


def audit_dataset(
    file_path: str,
    repo_path: str | None = None,
    sample: int = 50,
    seed: int = 1,
    out_doc: str = "docs/DATASET_AUDIT.md",
    input_func: Callable[[str], str] = input,
) -> AuditStats:
    """Interactively audit sampled buggy cases to calculate dataset label noise.

    Parameters
    ----------
    file_path:
        Path to the JSONL dataset file.
    repo_path:
        Optional path to the source git repository to show fix diffs.
    sample:
        Number of buggy cases to sample (default: 50).
    seed:
        Random seed for deterministic sampling (default: 1).
    out_doc:
        Path to the markdown report file (default: docs/DATASET_AUDIT.md).
    input_func:
        Input prompt function (defaults to built-in ``input``).

    Returns
    -------
    AuditStats
        Summary statistics of the audit verdicts.
    """
    cases = read_dataset(file_path)
    buggy_cases = [c for c in cases if c.label == "buggy"]

    if not buggy_cases:
        raise ValueError(f"No buggy cases found in dataset: {file_path}")

    # Deterministic sampling
    rng = random.Random(seed)  # nosec: B311  # pseudo-random sampling for dataset audit
    num_to_sample = min(sample, len(buggy_cases))
    sampled_cases = rng.sample(buggy_cases, num_to_sample)
    sampled_ids = [c.id for c in sampled_cases]

    verdicts: list[tuple[Case, str]] = []

    print(f"\nAuditing {num_to_sample} sampled buggy cases from {file_path} (seed={seed}).")
    print("For each case, review the diff and decide if it truly introduced a bug.\n")

    for idx, case in enumerate(sampled_cases, start=1):
        print("=" * 80)
        print(f"Case {idx} of {num_to_sample}: {case.id}")
        print(f"Commit SHA : {case.commit_sha}")
        print(f"Fix SHA    : {case.fix_sha or 'None'}")
        print(f"Locations  : {case.buggy_locations}")
        print("-" * 80)
        print("[INTRODUCING COMMIT DIFF]:")
        print(case.diff.strip())
        print("-" * 80)

        if repo_path and case.fix_sha:
            fix_diff = _get_fix_diff(repo_path, case.fix_sha)
            if fix_diff:
                print(f"[FIX COMMIT DIFF ({case.fix_sha[:10]})]:")
                # Show first 40 lines of fix diff to keep output readable
                fix_lines = fix_diff.splitlines()
                preview = "\n".join(fix_lines[:40])
                if len(fix_lines) > 40:
                    preview += f"\n... ({len(fix_lines) - 40} more lines)"
                print(preview)
                print("-" * 80)

        choice = ""
        while choice not in ("y", "n", "skip", "q"):
            raw = input_func("Was this really bug-introducing? [y = yes, n = no (noise), s = skip, q = quit]: ")
            cleaned = raw.strip().lower()
            if cleaned in ("y", "yes"):
                choice = "y"
            elif cleaned in ("n", "no"):
                choice = "n"
            elif cleaned in ("s", "skip"):
                choice = "skip"
            elif cleaned in ("q", "quit"):
                choice = "q"
            else:
                print("Invalid input. Please enter 'y', 'n', 'skip' (or 's'), or 'q' to quit.")

        if choice == "q":
            print("Audit stopped early by user.")
            break

        verdicts.append((case, choice))

    yes_count = sum(1 for _, v in verdicts if v == "y")
    no_count = sum(1 for _, v in verdicts if v == "n")
    skip_count = sum(1 for _, v in verdicts if v == "skip")
    total_evaluated = yes_count + no_count

    noise_rate = (no_count / total_evaluated * 100.0) if total_evaluated > 0 else 0.0

    # Write report
    report_path = Path(out_doc)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Dataset Label Noise Audit",
        "",
        "## Summary",
        f"{yes_count} of {total_evaluated} sampled buggy cases were really bug-introducing (noise rate {noise_rate:.1f}%).",
        "",
        "## Audit Parameters",
        f"- **Dataset file:** `{file_path}`",
        f"- **Source repository:** `{repo_path or 'not specified'}`",
        f"- **Sample size:** {sample}",
        f"- **Random seed:** {seed}",
        f"- **Evaluated cases:** {total_evaluated} ({yes_count} verified bug-introducing, {no_count} label noise)",
        f"- **Skipped cases:** {skip_count}",
        f"- **Noise rate:** {noise_rate:.1f}%",
        "",
        "## Evaluated Cases",
        "| # | Case ID | Commit SHA | Fix SHA | Verdict |",
        "|---|---|---|---|---|",
    ]

    for idx, (case, verdict) in enumerate(verdicts, start=1):
        lines.append(
            f"| {idx} | `{case.id}` | `{case.commit_sha[:10]}` | `{case.fix_sha[:10] if case.fix_sha else 'None'}` | `{verdict}` |"
        )

    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")

    stats = AuditStats(
        yes_count=yes_count,
        no_count=no_count,
        skip_count=skip_count,
        total_evaluated=total_evaluated,
        noise_rate=noise_rate,
        sampled_ids=sampled_ids,
        out_doc=str(report_path),
    )

    print("\n" + "=" * 80)
    print("Audit Complete!")
    print(
        f"{yes_count} of {total_evaluated} sampled buggy cases were really bug-introducing (noise rate {noise_rate:.1f}%)."
    )
    print(f"Results written to: {report_path}")
    print("=" * 80 + "\n")

    return stats
