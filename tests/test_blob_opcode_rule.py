from __future__ import annotations

from pathlib import Path

from arcaudit.domain import Confidence, Outcome, Severity
from arcaudit.profiles import load_profile
from arcaudit.services.scan import scan_project

_FIXTURE = Path(__file__).parents[1] / "lab" / "blob-opcode-assumption"
_EDGE_FIXTURE = Path(__file__).parents[1] / "lab" / "blob-opcode-assumption-edge"
_SAFE_FIXTURE = Path(__file__).parents[1] / "lab" / "blob-opcode-assumption-safe"


def test_scan_reports_arc_blob_opcode_assumptions() -> None:
    report = scan_project(_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    findings = [result for result in report.results if result.check_id == "ARC-EVM-002"]
    assert len(findings) == 2
    assert {finding.evidence[0].observed for finding in findings} == {
        "BLOBBASEFEE",
        "BLOBHASH",
    }
    assert all(finding.outcome is Outcome.FINDING for finding in findings)
    assert all(finding.severity is Severity.MEDIUM for finding in findings)
    assert all(finding.confidence is Confidence.HIGH for finding in findings)
    assert report.coverage.files_considered == 1
    assert report.coverage.files_analyzed == 1


def test_scan_reports_blob_opcodes_nested_in_expressions() -> None:
    report = scan_project(_EDGE_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    findings = [result for result in report.results if result.check_id == "ARC-EVM-002"]
    assert {finding.evidence[0].observed for finding in findings} == {
        "BLOBBASEFEE",
        "BLOBHASH",
    }


def test_scan_does_not_flag_externally_supplied_blob_data() -> None:
    report = scan_project(_SAFE_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    result = next(result for result in report.results if result.check_id == "ARC-EVM-002")
    assert result.outcome is Outcome.PASS
