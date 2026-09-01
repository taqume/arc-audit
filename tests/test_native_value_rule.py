from __future__ import annotations

from pathlib import Path

from arcaudit.domain import Confidence, Outcome, Severity
from arcaudit.profiles import load_profile
from arcaudit.services.scan import scan_project

_FIXTURE = Path(__file__).parents[1] / "lab" / "restricted-native-value-target"
_EDGE_FIXTURE = Path(__file__).parents[1] / "lab" / "restricted-native-value-target-edge"
_SAFE_FIXTURE = Path(__file__).parents[1] / "lab" / "restricted-native-value-target-safe"
_UNKNOWN_FIXTURE = Path(__file__).parents[1] / "lab" / "restricted-native-value-target-unknown"


def test_scan_reports_proven_forbidden_native_value_targets() -> None:
    report = scan_project(_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    findings = [result for result in report.results if result.check_id == "ARC-VALUE-001"]
    assert len(findings) == 2
    assert {finding.evidence[0].metadata["target_kind"] for finding in findings} == {
        "arc-precompile",
        "zero-address",
    }
    assert all(finding.outcome is Outcome.FINDING for finding in findings)
    assert all(finding.severity is Severity.MEDIUM for finding in findings)
    assert all(finding.confidence is Confidence.HIGH for finding in findings)


def test_scan_reports_constant_backed_forbidden_targets() -> None:
    report = scan_project(_EDGE_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    findings = [result for result in report.results if result.check_id == "ARC-VALUE-001"]
    assert len(findings) == 2
    assert {finding.evidence[0].metadata["call_kind"] for finding in findings} == {
        "call",
        "send",
    }


def test_scan_does_not_flag_zero_value_or_ordinary_transfers() -> None:
    report = scan_project(_SAFE_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    result = next(result for result in report.results if result.check_id == "ARC-VALUE-001")
    assert result.outcome is Outcome.PASS


def test_scan_reports_dynamic_positive_value_target_as_unknown() -> None:
    report = scan_project(_UNKNOWN_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    result = next(result for result in report.results if result.check_id == "ARC-VALUE-001")
    assert result.outcome is Outcome.UNKNOWN
    assert result.confidence is Confidence.HIGH
