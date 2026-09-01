from __future__ import annotations

from pathlib import Path

from arcaudit.domain import Outcome
from arcaudit.profiles import load_profile
from arcaudit.services.scan import scan_project

_INVALID_FIXTURE = Path(__file__).parents[1] / "lab" / "invalid-solidity"
_MALFORMED_LAYOUT_FIXTURE = Path(__file__).parents[1] / "lab" / "malformed-project-layout"
_UNSUPPORTED_COMPILER_FIXTURE = Path(__file__).parents[1] / "lab" / "unsupported-compiler"


def test_scan_reports_compilation_failure_without_claiming_rule_execution() -> None:
    report = scan_project(_INVALID_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    assert len(report.results) == 1
    assert report.results[0].check_id == "ARCAUDIT-SCAN-COMPILE-001"
    assert report.results[0].outcome is Outcome.ERROR
    assert report.results[0].summary.startswith("Slither analysis failed (")
    assert "InvalidContract" not in report.results[0].summary
    assert report.coverage.files_considered == 1
    assert report.coverage.files_analyzed == 0
    assert report.coverage.analyzers == ("slither",)
    assert report.coverage.skipped_reasons == ("Solidity compilation or Slither analysis failed.",)


def test_scan_reports_malformed_project_layout_as_bounded_error() -> None:
    report = scan_project(_MALFORMED_LAYOUT_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    assert report.results[0].check_id == "ARCAUDIT-SCAN-COMPILE-001"
    assert report.results[0].outcome is Outcome.ERROR
    assert report.coverage.files_considered == 1
    assert report.coverage.files_analyzed == 0
    assert report.coverage.analyzers == ("slither",)


def test_scan_reports_unsupported_compiler_as_bounded_error() -> None:
    report = scan_project(
        _UNSUPPORTED_COMPILER_FIXTURE, load_profile("arc-testnet"), allow_build=True
    )

    assert report.results[0].check_id == "ARCAUDIT-SCAN-COMPILE-001"
    assert report.results[0].outcome is Outcome.ERROR
    assert report.results[0].summary.startswith("Slither analysis failed (")
    assert "0.9.0" not in report.results[0].summary
    assert report.coverage.files_considered == 1
    assert report.coverage.files_analyzed == 0
