"""Source-scan application service and honest foundation coverage reporting."""

from __future__ import annotations

from pathlib import Path

from arcaudit.domain import (
    Applicability,
    CheckResult,
    Confidence,
    Coverage,
    Evidence,
    EvidenceType,
    Outcome,
    Report,
)
from arcaudit.engines.slither import SolidityAnalysisError, analyze_solidity_project
from arcaudit.profiles.models import NetworkProfile
from arcaudit.services.discovery import discover_files
from arcaudit.version import __version__


def scan_project(
    target: str | Path, profile: NetworkProfile, *, allow_build: bool = False
) -> Report:
    """Analyze Solidity only after the caller explicitly permits project compilation."""

    root = Path(target).expanduser().resolve()
    if not root.is_dir():
        result = CheckResult(
            check_id="ARCAUDIT-SCAN-INPUT-001",
            check_version="1.0.0",
            title="Scan target is readable",
            outcome=Outcome.ERROR,
            applicability=Applicability.UNKNOWN,
            confidence=Confidence.HIGH,
            summary=f"Scan target does not exist or is not a directory: {root}",
            evidence=(
                Evidence(
                    evidence_type=EvidenceType.NOT_CHECKED,
                    summary="No source analysis was executed.",
                    observed=str(root),
                    expected="an existing directory",
                ),
            ),
        )
        return Report.create(
            tool_version=__version__,
            command="scan",
            target=root,
            results=(result,),
            coverage=Coverage(skipped_reasons=("Scan target was unavailable.",)),
        )

    solidity_files = discover_files(root, (".sol",))
    if not solidity_files:
        result = CheckResult(
            check_id="ARCAUDIT-SCAN-ENGINE-001",
            check_version="1.0.0",
            title="Solidity detector execution",
            outcome=Outcome.NOT_APPLICABLE,
            applicability=Applicability.NOT_APPLICABLE,
            confidence=Confidence.HIGH,
            summary="No Solidity source files were discovered in the bounded project walk.",
            evidence=(
                Evidence(
                    evidence_type=EvidenceType.CONFIG_OBSERVED,
                    summary="Solidity source discovery completed.",
                    observed=0,
                    expected="one or more .sol files",
                ),
            ),
        )
        skipped_reasons: tuple[str, ...] = ()
    elif not allow_build:
        result = CheckResult(
            check_id="ARCAUDIT-SCAN-ENGINE-001",
            check_version="1.0.0",
            title="Solidity detector execution",
            outcome=Outcome.SKIPPED,
            applicability=Applicability.APPLICABLE,
            confidence=Confidence.HIGH,
            summary=(
                "Solidity files were discovered, but semantic detector execution requires "
                "explicit build permission. No source conclusion was produced."
            ),
            evidence=(
                Evidence(
                    evidence_type=EvidenceType.NOT_CHECKED,
                    summary="Source discovery ran; semantic detector execution did not.",
                    observed=len(solidity_files),
                    expected="validated Arc-specific detector rules",
                    metadata={
                        "profile_id": profile.profile_id,
                        "profile_revision": profile.revision,
                    },
                ),
            ),
        )
        skipped_reasons = (
            "Slither compilation was not allowed; rerun with explicit build permission.",
        )

    else:
        scan_results: tuple[CheckResult, ...]
        try:
            analysis = analyze_solidity_project(root, profile)
        except SolidityAnalysisError as error:
            result = CheckResult(
                check_id="ARCAUDIT-SCAN-COMPILE-001",
                check_version="1.0.0",
                title="Solidity analysis execution",
                outcome=Outcome.ERROR,
                applicability=Applicability.UNKNOWN,
                confidence=Confidence.HIGH,
                summary=str(error),
                evidence=(
                    Evidence(
                        evidence_type=EvidenceType.NOT_CHECKED,
                        summary="Slither could not produce semantic analysis evidence.",
                    ),
                ),
            )
            scan_results = (result,)
            analyzed_files = 0
            skipped_reasons = ("Solidity compilation or Slither analysis failed.",)
        else:
            scan_results = analysis.results
            analyzed_files = len(
                {source.resolve() for source in solidity_files} & analysis.source_files
            )
            skipped_reasons = ()

        return Report.create(
            tool_version=__version__,
            command="scan",
            target=root,
            results=scan_results,
            coverage=Coverage(
                files_considered=len(solidity_files),
                files_analyzed=analyzed_files,
                analyzers=("slither", "ARC-EVM-001", "ARC-EVM-002"),
                skipped_reasons=skipped_reasons,
            ),
        )

    return Report.create(
        tool_version=__version__,
        command="scan",
        target=root,
        results=(result,),
        coverage=Coverage(
            files_considered=len(solidity_files),
            files_analyzed=0,
            analyzers=("solidity-source-discovery",),
            skipped_reasons=skipped_reasons,
        ),
    )
