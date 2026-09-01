from __future__ import annotations

import json
from pathlib import Path

from arcaudit.cli import _report_exit_code, main
from arcaudit.domain import (
    Applicability,
    CheckResult,
    Coverage,
    Outcome,
    Report,
    Severity,
)


def test_profile_show_json(capsys: object) -> None:
    exit_code = main(["profile", "show", "arc-testnet", "--format", "json"])

    assert exit_code == 0
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    payload = json.loads(captured.out)
    assert payload["profile_id"] == "arc-testnet"
    assert payload["chain_id"] == 5_042_002


def test_exit_code_is_zero_only_for_completed_non_finding_outcomes() -> None:
    report = _report_with_outcomes(Outcome.PASS, Outcome.NOT_APPLICABLE)

    assert _report_exit_code(report) == 0


def test_exit_code_distinguishes_findings_errors_and_incomplete_evidence() -> None:
    assert _report_exit_code(_report_with_outcomes(Outcome.FINDING)) == 1
    assert _report_exit_code(_report_with_outcomes(Outcome.ERROR, Outcome.FINDING)) == 2
    assert _report_exit_code(_report_with_outcomes(Outcome.UNKNOWN)) == 3
    assert _report_exit_code(_report_with_outcomes(Outcome.SKIPPED)) == 3


def test_scan_without_build_permission_returns_incomplete_status(
    tmp_path: Path, capsys: object
) -> None:
    source = tmp_path / "src" / "Example.sol"
    source.parent.mkdir()
    source.write_text("pragma solidity ^0.8.24; contract Example {}\n", encoding="utf-8")

    exit_code = main(["scan", str(tmp_path), "--format", "json"])

    assert exit_code == 3
    payload = json.loads(capsys.readouterr().out)  # type: ignore[attr-defined]
    assert payload["summary"]["SKIPPED"] == 1


def _report_with_outcomes(*outcomes: Outcome) -> Report:
    results = tuple(
        CheckResult(
            check_id=f"TEST-{index}",
            check_version="1.0.0",
            title="Test result",
            outcome=outcome,
            applicability=Applicability.APPLICABLE,
            severity=Severity.MEDIUM if outcome is Outcome.FINDING else None,
            summary="Test result.",
        )
        for index, outcome in enumerate(outcomes)
    )
    return Report.create(
        tool_version="test",
        command="scan",
        target=".",
        results=results,
        coverage=Coverage(),
    )
