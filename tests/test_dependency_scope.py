from __future__ import annotations

from pathlib import Path

from arcaudit.domain import Outcome
from arcaudit.profiles import load_profile
from arcaudit.services.scan import scan_project

_FIXTURE = Path(__file__).parents[1] / "lab" / "dependency-scope"


def test_scan_excludes_dependency_only_unknowns_from_rule_results() -> None:
    report = scan_project(_FIXTURE, load_profile("arc-testnet"), allow_build=True)

    assert not any(result.outcome is Outcome.UNKNOWN for result in report.results)
    assert all(result.outcome is Outcome.PASS for result in report.results)
    assert report.coverage.files_considered == 1
    assert report.coverage.files_analyzed == 1
