from __future__ import annotations

import pytest

from arcaudit.domain import (
    Applicability,
    CheckResult,
    Confidence,
    Coverage,
    Outcome,
    Report,
    Severity,
)


def test_finding_requires_severity() -> None:
    with pytest.raises(ValueError, match="require a severity"):
        CheckResult(
            check_id="TEST-001",
            check_version="1.0.0",
            title="Test",
            outcome=Outcome.FINDING,
            applicability=Applicability.APPLICABLE,
            confidence=Confidence.HIGH,
            summary="Missing severity",
        )


def test_non_finding_rejects_severity() -> None:
    with pytest.raises(ValueError, match="only valid"):
        CheckResult(
            check_id="TEST-002",
            check_version="1.0.0",
            title="Test",
            outcome=Outcome.PASS,
            applicability=Applicability.APPLICABLE,
            severity=Severity.INFO,
            confidence=Confidence.HIGH,
            summary="Unexpected severity",
        )


def test_report_keeps_skipped_separate_from_pass() -> None:
    report = Report.create(
        tool_version="test",
        command="scan",
        target=".",
        results=(
            CheckResult(
                check_id="TEST-003",
                check_version="1.0.0",
                title="Skipped check",
                outcome=Outcome.SKIPPED,
                applicability=Applicability.UNKNOWN,
                summary="Not executed",
            ),
        ),
        coverage=Coverage(skipped_reasons=("Not executed",)),
    )

    assert report.counts()["SKIPPED"] == 1
    assert report.counts()["PASS"] == 0
    assert report.to_dict()["coverage"] == {
        "files_considered": 0,
        "files_analyzed": 0,
        "analyzers": [],
        "skipped_reasons": ["Not executed"],
    }
