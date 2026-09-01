from __future__ import annotations

from pathlib import Path

from arcaudit.domain import Outcome
from arcaudit.profiles import load_profile
from arcaudit.services.doctor import doctor_project
from arcaudit.services.scan import scan_project


def test_doctor_discovers_configs_without_executing_tools(tmp_path: Path) -> None:
    (tmp_path / "foundry.toml").write_text("[profile.default]\n", encoding="utf-8")
    (tmp_path / "hardhat.config.ts").write_text("export default {};\n", encoding="utf-8")

    report = doctor_project(tmp_path, load_profile("arc-testnet"))

    assert [result.outcome for result in report.results] == [
        Outcome.PASS,
        Outcome.PASS,
        Outcome.PASS,
    ]
    assert report.coverage.analyzers == ("project-discovery", "network-profile")


def test_doctor_marks_missing_tool_configs_not_applicable(tmp_path: Path) -> None:
    report = doctor_project(tmp_path, load_profile("arc-testnet"))

    assert report.results[1].outcome is Outcome.NOT_APPLICABLE
    assert report.results[2].outcome is Outcome.NOT_APPLICABLE


def test_scan_reports_detector_execution_as_skipped(tmp_path: Path) -> None:
    contract = tmp_path / "src" / "Example.sol"
    contract.parent.mkdir()
    contract.write_text("pragma solidity ^0.8.20; contract Example {}\n", encoding="utf-8")

    report = scan_project(tmp_path, load_profile("arc-testnet"))

    assert report.results[0].outcome is Outcome.SKIPPED
    assert report.coverage.files_considered == 1
    assert report.coverage.files_analyzed == 0


def test_scan_discovery_uses_production_source_boundary(tmp_path: Path) -> None:
    for directory in ("src", "lib", "script", "test"):
        contract = tmp_path / directory / f"{directory.title()}.sol"
        contract.parent.mkdir()
        contract.write_text(
            f"pragma solidity ^0.8.20; contract {directory.title()} {{}}\n",
            encoding="utf-8",
        )

    report = scan_project(tmp_path, load_profile("arc-testnet"))

    assert report.coverage.files_considered == 1
