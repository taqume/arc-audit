"""Detect proven nonzero native-value transfers to Arc-forbidden targets."""

from __future__ import annotations

from slither.slither import Slither
from slither.slithir.operations import LowLevelCall, Operation, Send, Transfer

from arcaudit.domain import (
    Applicability,
    CheckResult,
    Confidence,
    Evidence,
    EvidenceType,
    Outcome,
    Severity,
)
from arcaudit.profiles.models import NetworkProfile
from arcaudit.rules._slither_values import resolve_constant_int

_RULE_ID = "ARC-VALUE-001"
_RULE_VERSION = "1.0.0"
_SOURCE_URLS = (
    "https://docs.arc.io/arc/references/evm-differences#value-transfer-rules",
    "https://docs.arc.io/arc/concepts/execution-layer#protocol-precompiles",
)


def evaluate_native_value_targets(
    slither: Slither, profile: NetworkProfile
) -> tuple[CheckResult, ...]:
    """Find statically proven nonzero transfers to zero or known Arc precompiles."""

    precompiles = {
        int(record.address, 16)
        for record in profile.addresses
        if record.kind == "protocol-precompile"
    }
    results: list[CheckResult] = []
    seen_locations: set[tuple[str, tuple[int, ...], int]] = set()
    for contract in slither.contracts:
        for function in contract.functions_and_modifiers:
            for node in function.nodes:
                for operation in node.irs:
                    if not isinstance(operation, (LowLevelCall, Send, Transfer)):
                        continue
                    amount = resolve_constant_int(operation.call_value, node.irs)
                    target = resolve_constant_int(operation.destination, node.irs)
                    target_kind = _target_kind(target, precompiles)
                    if amount is None or amount <= 0 or target is None or target_kind is None:
                        continue
                    source = node.source_mapping
                    location = (source.filename.short, tuple(source.lines), target)
                    if location in seen_locations:
                        continue
                    seen_locations.add(location)
                    source_line = source.lines[0] if source.lines else None
                    target_label = (
                        "the zero address" if target_kind == "zero-address" else "an Arc precompile"
                    )
                    results.append(
                        CheckResult(
                            check_id=_RULE_ID,
                            check_version=_RULE_VERSION,
                            title="Arc-forbidden native-value target",
                            outcome=Outcome.FINDING,
                            applicability=Applicability.APPLICABLE,
                            severity=Severity.MEDIUM,
                            confidence=Confidence.HIGH,
                            summary=(
                                "A statically nonzero native-value transfer targets "
                                f"{target_label}. Arc rejects this transfer "
                                "even when the sender has sufficient balance."
                            ),
                            evidence=(
                                Evidence(
                                    evidence_type=EvidenceType.STATIC_PROVEN,
                                    summary="Slither resolved both the destination and value.",
                                    observed=f"0x{target:040x}",
                                    expected=(
                                        "zero value or a destination that accepts native value"
                                    ),
                                    source=(
                                        f"{source.filename.short}:{source_line}"
                                        if source_line is not None
                                        else source.filename.short
                                    ),
                                    metadata={
                                        "source_path": source.filename.short,
                                        "source_lines": list(source.lines),
                                        "contract": contract.name,
                                        "function": function.canonical_name,
                                        "call_kind": _call_kind(operation),
                                        "native_value": amount,
                                        "target_kind": target_kind,
                                        "category": "compatibility",
                                        "profile_id": profile.profile_id,
                                        "profile_revision": profile.revision,
                                    },
                                ),
                            ),
                            source_urls=_SOURCE_URLS,
                        )
                    )

    if results:
        return tuple(results)
    return (
        CheckResult(
            check_id=_RULE_ID,
            check_version=_RULE_VERSION,
            title="Arc-forbidden native-value target",
            outcome=Outcome.PASS,
            applicability=Applicability.APPLICABLE,
            confidence=Confidence.HIGH,
            summary=(
                "No statically nonzero native-value transfer resolved to the zero address or "
                "a known Arc precompile in the analyzed Slither IR."
            ),
            evidence=(
                Evidence(
                    evidence_type=EvidenceType.STATIC_PROVEN,
                    summary="The rule completed over the analyzed Slither IR.",
                    observed=0,
                    expected=0,
                    metadata={
                        "profile_id": profile.profile_id,
                        "profile_revision": profile.revision,
                    },
                ),
            ),
            source_urls=_SOURCE_URLS,
        ),
    )


def _target_kind(target: int | None, precompiles: set[int]) -> str | None:
    """Classify only targets whose Arc revert behavior is profile-backed."""

    if target == 0:
        return "zero-address"
    if target in precompiles:
        return "arc-precompile"
    return None


def _call_kind(operation: Operation) -> str:
    """Return a stable call label for evidence consumers."""

    if isinstance(operation, LowLevelCall):
        return str(operation.function_name)
    if isinstance(operation, Send):
        return "send"
    return "transfer"
