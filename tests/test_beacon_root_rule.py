from __future__ import annotations

from pathlib import Path

from arcaudit.domain import Confidence, Outcome, Severity
from arcaudit.profiles import load_profile
from arcaudit.services.scan import scan_project

_FIXTURE = Path(__file__).parents[1] / "lab" / "beacon-root-assumption"
_DIRECT_LITERAL_FIXTURE = _FIXTURE / "direct-literal"
_SAFE_FIXTURE = _FIXTURE / "safe"
_UNKNOWN_FIXTURE = Path(__file__).parents[1] / "lab" / "beacon-root-assumption-unknown"


def test_scan_reports_direct_ethereum_beacon_root_call() -> None:
    report = scan_project(_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    finding = next(result for result in report.results if result.check_id == "ARC-EVM-001")
    assert finding.outcome is Outcome.FINDING
    assert finding.severity is Severity.MEDIUM
    assert finding.confidence is Confidence.HIGH
    assert finding.evidence[0].metadata["source_path"] == ("src/VulnerableBeaconRootConsumer.sol")
    assert report.coverage.files_considered == 3
    assert report.coverage.files_analyzed == 1
    assert report.coverage.skipped_reasons == (
        "Slither compiled 1 of 3 discovered Solidity files; 2 files remain unanalyzed.",
    )


def test_scan_reports_direct_literal_beacon_root_call() -> None:
    report = scan_project(_DIRECT_LITERAL_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    finding = next(result for result in report.results if result.check_id == "ARC-EVM-001")
    assert finding.outcome is Outcome.FINDING
    assert finding.confidence is Confidence.HIGH
    assert finding.evidence[0].metadata["source_path"] == "src/DirectBeaconRootConsumer.sol"


def test_scan_does_not_flag_unused_ethereum_address() -> None:
    report = scan_project(_SAFE_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    result = next(result for result in report.results if result.check_id == "ARC-EVM-001")
    assert result.outcome is Outcome.PASS
    assert report.coverage.files_considered == 1
    assert report.coverage.files_analyzed == 1


def test_scan_reports_configurable_low_level_target_as_unknown() -> None:
    report = scan_project(_UNKNOWN_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    result = next(result for result in report.results if result.check_id == "ARC-EVM-001")
    assert result.outcome is Outcome.UNKNOWN
    assert result.confidence is Confidence.HIGH
