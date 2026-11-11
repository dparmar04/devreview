"""Tests for dataset audit tool (T-106)."""

from __future__ import annotations

import json
from pathlib import Path

from devreview.dataset.audit import audit_dataset
from devreview.dataset.builder import Case


def _create_mock_dataset(path: Path, count: int = 10) -> Path:
    cases = []
    for i in range(count):
        cases.append(
            Case(
                id=f"case_{i}",
                repo="mock_repo",
                commit_sha=f"{i:040x}",
                parent_sha=f"{i + 1:040x}",
                label="buggy",
                fix_sha=f"{i + 100:040x}",
                buggy_locations=[{"file": "app.py", "introducing_sha": f"{i:040x}", "start_line": 1, "end_line": 2}],
                diff="--- a/app.py\n+++ b/app.py\n@@ -1,1 +1,1 @@\n- bad\n+ good\n",
            )
        )
    with path.open("w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps(c.to_dict()) + "\n")
    return path


def test_audit_dataset_logic_and_output(tmp_path: Path) -> None:
    data_file = _create_mock_dataset(tmp_path / "data.jsonl", count=10)
    audit_file = tmp_path / "DATASET_AUDIT.md"

    # Simulate user input: 3 yes, 1 no, 1 skip for a sample of 5
    answers = iter(["y", "y", "n", "skip", "y"])

    stats = audit_dataset(
        file_path=str(data_file),
        repo_path=None,
        sample=5,
        seed=42,
        out_doc=str(audit_file),
        input_func=lambda prompt: next(answers),
    )

    assert stats.yes_count == 3
    assert stats.no_count == 1
    assert stats.skip_count == 1
    assert stats.total_evaluated == 4
    # Noise rate: 1 of 4 was false = 25.0%
    assert abs(stats.noise_rate - 25.0) < 0.01

    assert audit_file.exists()
    content = audit_file.read_text(encoding="utf-8")
    expected_statement = "3 of 4 sampled buggy cases were really bug-introducing (noise rate 25.0%)"
    assert expected_statement in content


def test_audit_dataset_deterministic_seed(tmp_path: Path) -> None:
    data_file = _create_mock_dataset(tmp_path / "data.jsonl", count=20)
    audit1 = tmp_path / "audit1.md"
    audit2 = tmp_path / "audit2.md"

    answers1 = iter(["y"] * 5)
    stats1 = audit_dataset(
        file_path=str(data_file),
        sample=5,
        seed=123,
        out_doc=str(audit1),
        input_func=lambda p: next(answers1),
    )

    answers2 = iter(["y"] * 5)
    stats2 = audit_dataset(
        file_path=str(data_file),
        sample=5,
        seed=123,
        out_doc=str(audit2),
        input_func=lambda p: next(answers2),
    )

    assert stats1.sampled_ids == stats2.sampled_ids
