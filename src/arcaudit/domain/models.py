"""Framework-independent result and evidence contracts used by every adapter."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import TypeAlias

JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


class Outcome(StrEnum):
    """Result of an individual ArcAudit check."""

    PASS = "PASS"
    FINDING = "FINDING"
    UNKNOWN = "UNKNOWN"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class Severity(StrEnum):
    """Impact assigned only when a check produces a finding."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class Confidence(StrEnum):
    """Strength of the connection between evidence and the reported outcome."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Applicability(StrEnum):
    """Whether a check applies to the analyzed target and profile."""

    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class EvidenceType(StrEnum):
    """How ArcAudit observed or established a result."""

    STATIC_PROVEN = "STATIC_PROVEN"
    CONFIG_OBSERVED = "CONFIG_OBSERVED"
    RPC_OBSERVED = "RPC_OBSERVED"
    LIVE_TX_OBSERVED = "LIVE_TX_OBSERVED"
    USER_ASSERTED = "USER_ASSERTED"
    NOT_CHECKED = "NOT_CHECKED"


@dataclass(frozen=True, slots=True)
class Evidence:
    """A bounded fact supporting one check result."""

    evidence_type: EvidenceType
    summary: str
    observed: JsonValue = None
    expected: JsonValue = None
    source: str | None = None
    metadata: dict[str, JsonValue] = field(default_factory=dict)

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a stable JSON-compatible representation."""

        return {
            "type": self.evidence_type.value,
            "summary": self.summary,
            "observed": self.observed,
            "expected": self.expected,
            "source": self.source,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class CheckResult:
    """Result of one versioned rule, doctor check, or protocol probe."""

    check_id: str
    check_version: str
    title: str
    outcome: Outcome
    applicability: Applicability
    summary: str
    severity: Severity | None = None
    confidence: Confidence | None = None
    evidence: tuple[Evidence, ...] = ()
    source_urls: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Prevent severity from leaking into non-finding outcomes."""

        if self.outcome is Outcome.FINDING and self.severity is None:
            raise ValueError("FINDING outcomes require a severity")
        if self.outcome is not Outcome.FINDING and self.severity is not None:
            raise ValueError("severity is only valid for FINDING outcomes")

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a stable JSON-compatible representation."""

        return {
            "check_id": self.check_id,
            "check_version": self.check_version,
            "title": self.title,
            "outcome": self.outcome.value,
            "applicability": self.applicability.value,
            "summary": self.summary,
            "severity": self.severity.value if self.severity else None,
            "confidence": self.confidence.value if self.confidence else None,
            "evidence": [item.to_dict() for item in self.evidence],
            "source_urls": list(self.source_urls),
        }


@dataclass(frozen=True, slots=True)
class Coverage:
    """Scope that ArcAudit did and did not inspect."""

    files_considered: int = 0
    files_analyzed: int = 0
    analyzers: tuple[str, ...] = ()
    skipped_reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Reject impossible coverage counters."""

        if self.files_considered < 0 or self.files_analyzed < 0:
            raise ValueError("coverage counters cannot be negative")
        if self.files_analyzed > self.files_considered:
            raise ValueError("files_analyzed cannot exceed files_considered")

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a stable JSON-compatible representation."""

        return {
            "files_considered": self.files_considered,
            "files_analyzed": self.files_analyzed,
            "analyzers": list(self.analyzers),
            "skipped_reasons": list(self.skipped_reasons),
        }


@dataclass(frozen=True, slots=True)
class NetworkObservation:
    """Network identity observed during an online check."""

    profile_id: str
    profile_revision: str
    endpoint: str
    chain_id: int | None = None
    block_number: int | None = None
    block_timestamp: int | None = None

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a stable JSON-compatible representation."""

        return {
            "profile_id": self.profile_id,
            "profile_revision": self.profile_revision,
            "endpoint": self.endpoint,
            "chain_id": self.chain_id,
            "block_number": self.block_number,
            "block_timestamp": self.block_timestamp,
        }


@dataclass(frozen=True, slots=True)
class Report:
    """Top-level report shared by the CLI, SDK, MCP, and future CI adapters."""

    schema_version: str
    tool_version: str
    command: str
    target: str
    generated_at: str
    results: tuple[CheckResult, ...]
    coverage: Coverage
    network: NetworkObservation | None = None

    @classmethod
    def create(
        cls,
        *,
        tool_version: str,
        command: str,
        target: str | Path,
        results: tuple[CheckResult, ...],
        coverage: Coverage,
        network: NetworkObservation | None = None,
    ) -> Report:
        """Create a report with the current schema and a UTC timestamp."""

        return cls(
            schema_version="1.0.0",
            tool_version=tool_version,
            command=command,
            target=str(target),
            generated_at=datetime.now(UTC).isoformat(),
            results=results,
            coverage=coverage,
            network=network,
        )

    def counts(self) -> dict[str, int]:
        """Count outcomes without collapsing unknown or skipped work into pass."""

        counts = {outcome.value: 0 for outcome in Outcome}
        for result in self.results:
            counts[result.outcome.value] += 1
        return counts

    def to_dict(self) -> dict[str, JsonValue]:
        """Return the versioned JSON report contract."""

        summary: dict[str, JsonValue] = {outcome: count for outcome, count in self.counts().items()}
        return {
            "schema_version": self.schema_version,
            "tool_version": self.tool_version,
            "command": self.command,
            "target": self.target,
            "generated_at": self.generated_at,
            "summary": summary,
            "results": [result.to_dict() for result in self.results],
            "coverage": self.coverage.to_dict(),
            "network": self.network.to_dict() if self.network else None,
        }
