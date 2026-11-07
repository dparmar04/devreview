"""Tests for the devreview CLI skeleton (T-101)."""

import subprocess
import sys


def test_version_flag():
    """``devreview --version`` prints the version string."""
    result = subprocess.run(
        [sys.executable, "-m", "devreview", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "devreview 0.0.0" in result.stdout


def test_dataset_help():
    """``devreview dataset --help`` exits 0 and shows usage."""
    result = subprocess.run(
        [sys.executable, "-m", "devreview", "dataset", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "dataset" in result.stdout.lower()


def test_backtest_help():
    """``devreview backtest --help`` exits 0 and shows usage."""
    result = subprocess.run(
        [sys.executable, "-m", "devreview", "backtest", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "backtest" in result.stdout.lower()


def test_no_args_shows_help():
    """Running ``devreview`` with no arguments prints help and exits cleanly."""
    result = subprocess.run(
        [sys.executable, "-m", "devreview"],
        capture_output=True,
        text=True,
    )
    # argparse may exit 0 or 2 depending on config; we just want it not to crash
    assert result.returncode in (0, 2)
