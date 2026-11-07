"""CLI entry point for devreview.

Uses only the standard library ``argparse`` module.
Subcommand groups ``dataset`` and ``backtest`` are placeholders
that will gain real sub-commands in later phases.
"""

from __future__ import annotations

import argparse

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
    subparsers.add_parser(
        "dataset",
        help="Build and inspect golden datasets from git history.",
    )

    # -- backtest subcommand group --
    subparsers.add_parser(
        "backtest",
        help="Run and compare LLM review back-tests.",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    """Parse arguments and dispatch.  Called by the console-script entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()


if __name__ == "__main__":
    main()
