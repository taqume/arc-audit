from __future__ import annotations

from pathlib import Path

from arcaudit.domain import Confidence, Outcome, Severity
from arcaudit.profiles import load_profile
from arcaudit.services.scan import scan_project

_FIXTURE = Path(__file__).parents[1] / "lab" / "selfdestruct-beneficiary"
_EDGE_FIXTURE = Path(__file__).parents[1] / "lab" / "selfdestruct-beneficiary-edge"
_SAFE_FIXTURE = Path(__file__).parents[1] / "lab" / "selfdestruct-beneficiary-safe"
_UNKNOWN_FIXTURE = Path(__file__).parents[1] / "lab" / "selfdestruct-beneficiary-unknown"


def test_scan_reports_proven_restricted_selfdestruct_beneficiaries() -> None:
    report = scan_project(_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    findings = [result for result in report.results if result.check_id == "ARC-SELFDESTRUCT-001"]
    assert len(findings) == 4
    assert {finding.evidence[0].metadata["beneficiary_kind"] for finding in findings} == {
        "arc-precompile",
        "blocklisted-test-address",
        "self",
        "zero-address",
    }
    assert all(finding.outcome is Outcome.FINDING for finding in findings)
    assert all(finding.severity is Severity.MEDIUM for finding in findings)
    assert all(finding.confidence is Confidence.HIGH for finding in findings)
    assert report.coverage.analyzers == (
        "slither",
        "ARC-EVM-001",
        "ARC-EVM-002",
        "ARC-VALUE-001",
        "ARC-SELFDESTRUCT-001",
    )


def test_scan_reports_constant_restricted_selfdestruct_beneficiaries() -> None:
    report = scan_project(_EDGE_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    findings = [result for result in report.results if result.check_id == "ARC-SELFDESTRUCT-001"]
    assert len(findings) == 2
    assert {finding.evidence[0].metadata["beneficiary_kind"] for finding in findings} == {
        "blocklisted-test-address",
        "zero-address",
    }


def test_scan_does_not_flag_permitted_selfdestruct_beneficiary() -> None:
    report = scan_project(_SAFE_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    result = next(result for result in report.results if result.check_id == "ARC-SELFDESTRUCT-001")
    assert result.outcome is Outcome.PASS


def test_scan_reports_dynamic_selfdestruct_beneficiary_as_unknown() -> None:
    report = scan_project(_UNKNOWN_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    result = next(result for result in report.results if result.check_id == "ARC-SELFDESTRUCT-001")
    assert result.outcome is Outcome.UNKNOWN
    assert result.confidence is Confidence.HIGH
