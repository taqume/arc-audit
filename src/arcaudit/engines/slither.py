"""Slither adapter that translates semantic analysis into ArcAudit results."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from slither.slither import Slither

from arcaudit.domain import CheckResult
from arcaudit.profiles.models import NetworkProfile
from arcaudit.rules.beacon_root import evaluate_beacon_root_assumption
from arcaudit.rules.blob_opcodes import evaluate_blob_opcode_assumptions
from arcaudit.rules.native_value import evaluate_native_value_targets
from arcaudit.rules.selfdestruct import evaluate_selfdestruct_beneficiaries


class SolidityAnalysisError(RuntimeError):
    """Raised when the external Solidity analysis engine cannot complete."""


@dataclass(frozen=True, slots=True)
class SlitherAnalysis:
    """Rule results and the exact source files Slither compiled."""

    results: tuple[CheckResult, ...]
    source_files: frozenset[Path]


def analyze_solidity_project(root: Path, profile: NetworkProfile) -> SlitherAnalysis:
    """Compile and analyze a project after the caller explicitly permits build execution."""

    try:
        slither = Slither(str(root))
    except Exception as error:
        # Compiler frameworks are an external trust boundary. Keep their raw output out of reports.
        raise SolidityAnalysisError(f"Slither analysis failed ({type(error).__name__})") from error

    results = (
        *evaluate_beacon_root_assumption(slither, profile),
        *evaluate_blob_opcode_assumptions(slither, profile),
        *evaluate_native_value_targets(slither, profile),
        *evaluate_selfdestruct_beneficiaries(slither, profile),
    )
    return SlitherAnalysis(
        results=results,
        source_files=frozenset(Path(source).resolve() for source in slither.source_code),
    )
