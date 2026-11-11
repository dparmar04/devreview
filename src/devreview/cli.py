"""CLI entry point for devreview.

Uses only the standard library ``argparse`` module.
"""

from __future__ import annotations

import argparse
from typing import Sequence

from devreview import __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="devreview",
        description="AI code reviewer that backtests itself on your repo's git history.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"devreview {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    # -- dataset subcommand group --
    dataset_parser = subparsers.add_parser(
        "dataset",
        help="Build and inspect golden datasets from git history.",
    )
    dataset_subparsers = dataset_parser.add_subparsers(dest="subcommand")

    # devreview dataset build <repo> --out ...
    build_parser = dataset_subparsers.add_parser(
        "build",
        help="Build golden dataset from a git repository.",
    )
    build_parser.add_argument(
        "repo",
        help="Path to git repository",
    )
    build_parser.add_argument(
        "--out",
        required=True,
        help="Output JSONL file path",
    )
    build_parser.add_argument(
        "--max-diff-lines",
        type=int,
        default=400,
        help="Skip diffs exceeding this line count (default: 400)",
    )
    build_parser.add_argument(
        "--min-age-days",
        type=int,
        default=90,
        help="Minimum age in days for clean cases (default: 90)",
    )

    # devreview dataset audit <file> --sample 50 --seed 1
    audit_parser = dataset_subparsers.add_parser(
        "audit",
        help="Interactively audit sampled buggy cases to calculate label noise.",
    )
    audit_parser.add_argument(
        "file",
        help="Path to dataset JSONL file",
    )
    audit_parser.add_argument(
        "--repo",
        default=None,
        help="Path to git repository to display fix commit diffs",
    )
    audit_parser.add_argument(
        "--sample",
        type=int,
        default=50,
        help="Number of cases to audit (default: 50)",
    )
    audit_parser.add_argument(
        "--seed",
        type=int,
        default=1,
        help="Random seed for sampling (default: 1)",
    )
    audit_parser.add_argument(
        "--out",
        default="docs/DATASET_AUDIT.md",
        help="Path to output markdown report (default: docs/DATASET_AUDIT.md)",
    )

    # -- backtest subcommand group --
    subparsers.add_parser(
        "backtest",
        help="Run and compare LLM review back-tests.",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """Parse arguments and dispatch. Called by the console-script entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return

    if args.command == "dataset":
        subcommand = getattr(args, "subcommand", None)
        if subcommand == "build":
            from devreview.dataset.builder import build_dataset

            stats = build_dataset(
                repo_path=args.repo,
                out_path=args.out,
                max_diff_lines=args.max_diff_lines,
                min_age_days=args.min_age_days,
            )
            print(
                f"Dataset built: {stats.buggy_count} buggy, {stats.clean_count} clean, "
                f"{stats.skipped_count} skipped -> {stats.out_path}"
            )
            return

        if subcommand == "audit":
            from devreview.dataset.audit import audit_dataset

            audit_dataset(
                file_path=args.file,
                repo_path=args.repo,
                sample=args.sample,
                seed=args.seed,
                out_doc=args.out,
            )
            return

        # No subcommand given under dataset
        # Retrieve the dataset parser to print its help
        for action in parser._subparsers._actions:  # type: ignore[attr-defined]
            if isinstance(action, argparse._SubParsersAction) and "dataset" in action.choices:
                action.choices["dataset"].print_help()
                return


if __name__ == "__main__":
    main()
