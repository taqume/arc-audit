"""Slither adapter that translates semantic analysis into ArcAudit results."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from slither.slither import Slither

from arcaudit.domain import CheckResult
from arcaudit.profiles.models import NetworkProfile
from arcaudit.rules.registry import SLITHER_RULES


class SolidityAnalysisError(RuntimeError):
    """Raised when the external Solidity analysis engine cannot complete."""


@dataclass(frozen=True, slots=True)
class SlitherAnalysis:
    """Rule results and the exact source files Slither compiled."""

    results: tuple[CheckResult, ...]
    source_files: frozenset[Path]
    rule_ids: tuple[str, ...]


def analyze_solidity_project(root: Path, profile: NetworkProfile) -> SlitherAnalysis:
    """Compile and analyze a project after the caller explicitly permits build execution."""

    try:
        slither = Slither(str(root))
    except Exception as error:
        # Compiler frameworks are an external trust boundary. Keep their raw output out of reports.
        raise SolidityAnalysisError(f"Slither analysis failed ({type(error).__name__})") from error

    results = tuple(result for rule in SLITHER_RULES for result in rule.evaluate(slither, profile))
    return SlitherAnalysis(
        results=results,
        source_files=frozenset(Path(source).resolve() for source in slither.source_code),
        rule_ids=tuple(rule.rule_id for rule in SLITHER_RULES),
    )
