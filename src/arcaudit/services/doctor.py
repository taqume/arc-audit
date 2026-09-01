"""Offline project diagnostics that never execute target-project commands."""

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
from arcaudit.domain.models import JsonValue
from arcaudit.profiles.models import NetworkProfile
from arcaudit.version import __version__

_HARDHAT_CONFIG_NAMES = (
    "hardhat.config.js",
    "hardhat.config.cjs",
    "hardhat.config.mjs",
    "hardhat.config.ts",
)


def doctor_project(target: str | Path, profile: NetworkProfile) -> Report:
    """Inspect recognized project configuration without running project code."""

    root = Path(target).expanduser().resolve()
    if not root.is_dir():
        result = CheckResult(
            check_id="ARCAUDIT-PROJECT-001",
            check_version="1.0.0",
            title="Project directory is readable",
            outcome=Outcome.ERROR,
            applicability=Applicability.UNKNOWN,
            confidence=Confidence.HIGH,
            summary=f"Project directory does not exist or is not a directory: {root}",
            evidence=(
                Evidence(
                    evidence_type=EvidenceType.CONFIG_OBSERVED,
                    summary="Target path validation failed.",
                    observed=str(root),
                    expected="an existing directory",
                ),
            ),
        )
        return Report.create(
            tool_version=__version__,
            command="doctor",
            target=root,
            results=(result,),
            coverage=Coverage(skipped_reasons=("Project directory was unavailable.",)),
        )

    foundry_config = root / "foundry.toml"
    hardhat_configs = tuple(root / name for name in _HARDHAT_CONFIG_NAMES)
    foundry_result = _tool_config_result(
        check_id="ARCAUDIT-TOOL-FOUNDRY-001",
        title="Foundry project configuration",
        tool_name="Foundry",
        paths=(foundry_config,),
        root=root,
    )
    hardhat_result = _tool_config_result(
        check_id="ARCAUDIT-TOOL-HARDHAT-001",
        title="Hardhat project configuration",
        tool_name="Hardhat",
        paths=hardhat_configs,
        root=root,
    )
    profile_result = CheckResult(
        check_id="ARCAUDIT-PROFILE-001",
        check_version="1.0.0",
        title="Selected Arc network profile",
        outcome=Outcome.PASS,
        applicability=Applicability.APPLICABLE,
        confidence=Confidence.HIGH,
        summary=(
            f"Loaded reviewed profile {profile.profile_id} revision {profile.revision} "
            f"for chain {profile.chain_id}."
        ),
        evidence=(
            Evidence(
                evidence_type=EvidenceType.CONFIG_OBSERVED,
                summary="ArcAudit loaded bundled, versioned profile data.",
                observed={
                    "profile_id": profile.profile_id,
                    "revision": profile.revision,
                    "chain_id": profile.chain_id,
                    "verified_at": profile.verified_at,
                },
                expected=profile.profile_id,
            ),
        ),
        source_urls=profile.source_urls,
    )
    inspected = 1 + len(_HARDHAT_CONFIG_NAMES)
    return Report.create(
        tool_version=__version__,
        command="doctor",
        target=root,
        results=(profile_result, foundry_result, hardhat_result),
        coverage=Coverage(
            files_considered=inspected,
            files_analyzed=inspected,
            analyzers=("project-discovery", "network-profile"),
        ),
    )


def _tool_config_result(
    *,
    check_id: str,
    title: str,
    tool_name: str,
    paths: tuple[Path, ...],
    root: Path,
) -> CheckResult:
    """Report tool applicability from root-level configuration files."""

    detected = tuple(path for path in paths if path.is_file())
    relative_paths: list[JsonValue] = [str(path.relative_to(root)) for path in detected]
    if detected:
        return CheckResult(
            check_id=check_id,
            check_version="1.0.0",
            title=title,
            outcome=Outcome.PASS,
            applicability=Applicability.APPLICABLE,
            confidence=Confidence.HIGH,
            summary=f"Detected {tool_name} configuration without executing project commands.",
            evidence=(
                Evidence(
                    evidence_type=EvidenceType.CONFIG_OBSERVED,
                    summary=f"Found {tool_name} configuration file.",
                    observed=relative_paths,
                    expected=f"a recognized {tool_name} configuration path",
                ),
            ),
        )
    return CheckResult(
        check_id=check_id,
        check_version="1.0.0",
        title=title,
        outcome=Outcome.NOT_APPLICABLE,
        applicability=Applicability.NOT_APPLICABLE,
        confidence=Confidence.HIGH,
        summary=f"No recognized root-level {tool_name} configuration was found.",
        evidence=(
            Evidence(
                evidence_type=EvidenceType.CONFIG_OBSERVED,
                summary=f"Checked known {tool_name} configuration names.",
                observed=[],
                expected=[str(path.name) for path in paths],
            ),
        ),
    )
