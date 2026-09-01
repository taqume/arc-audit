"""Detect direct dependencies on Ethereum's omitted EIP-4788 beacon-roots contract."""

from __future__ import annotations

from slither.core.source_mapping.source_mapping import Source
from slither.slither import Slither
from slither.slithir.operations import LowLevelCall

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

_RULE_ID = "ARC-EVM-001"
_RULE_VERSION = "1.0.0"
_ETHEREUM_BEACON_ROOTS = int("000F3df6D732807Ef1319fB7B8bB8522d0Beac02", 16)
_SOURCE_URL = "https://docs.arc.io/arc/references/evm-differences#execution-and-opcode-differences"


def evaluate_beacon_root_assumption(
    slither: Slither, profile: NetworkProfile
) -> tuple[CheckResult, ...]:
    """Find low-level calls to the Ethereum EIP-4788 system-contract address."""

    results: list[CheckResult] = []
    unresolved_results: list[CheckResult] = []
    for contract in slither.contracts:
        for function in contract.functions_and_modifiers:
            for node in function.nodes:
                for operation in node.irs:
                    if not isinstance(operation, LowLevelCall):
                        continue
                    resolved_address = resolve_constant_int(operation.destination, node.irs)
                    if resolved_address is None:
                        unresolved_results.append(
                            _unknown_destination_result(
                                contract.name,
                                function.canonical_name,
                                str(operation.function_name),
                                node.source_mapping,
                                profile,
                            )
                        )
                        continue
                    if resolved_address != _ETHEREUM_BEACON_ROOTS:
                        continue
                    source = node.source_mapping
                    source_line = source.lines[0] if source.lines else None
                    results.append(
                        CheckResult(
                            check_id=_RULE_ID,
                            check_version=_RULE_VERSION,
                            title="Ethereum beacon-roots contract dependency",
                            outcome=Outcome.FINDING,
                            applicability=Applicability.APPLICABLE,
                            severity=Severity.MEDIUM,
                            confidence=Confidence.HIGH,
                            summary=(
                                "A low-level call targets Ethereum's EIP-4788 beacon-roots "
                                "contract, which Arc omits. The call returns empty data on the "
                                "selected Arc profile."
                            ),
                            evidence=(
                                Evidence(
                                    evidence_type=EvidenceType.STATIC_PROVEN,
                                    summary=(
                                        "Slither resolved the low-level call destination to the "
                                        "Ethereum beacon-roots system address."
                                    ),
                                    observed=f"0x{resolved_address:040x}",
                                    expected="no dependency on Ethereum's EIP-4788 contract",
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
                                        "call_kind": str(operation.function_name),
                                        "category": "compatibility",
                                        "profile_id": profile.profile_id,
                                        "profile_revision": profile.revision,
                                    },
                                ),
                            ),
                            source_urls=(_SOURCE_URL,),
                        )
                    )

    if results or unresolved_results:
        return (*results, *unresolved_results)
    return (
        CheckResult(
            check_id=_RULE_ID,
            check_version=_RULE_VERSION,
            title="Ethereum beacon-roots contract dependency",
            outcome=Outcome.PASS,
            applicability=Applicability.APPLICABLE,
            confidence=Confidence.HIGH,
            summary=(
                "No low-level call resolved to Ethereum's EIP-4788 beacon-roots address in "
                "the analyzed Slither IR."
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
            source_urls=(_SOURCE_URL,),
        ),
    )


def _unknown_destination_result(
    contract_name: str,
    function_name: str,
    call_kind: str,
    source: Source,
    profile: NetworkProfile,
) -> CheckResult:
    """Represent an unresolved low-level destination without producing a false pass."""

    source_lines = list(source.lines)
    source_path = str(source.filename.short)
    source_line = source_lines[0] if source_lines else None
    return CheckResult(
        check_id=_RULE_ID,
        check_version=_RULE_VERSION,
        title="Ethereum beacon-roots contract dependency",
        outcome=Outcome.UNKNOWN,
        applicability=Applicability.UNKNOWN,
        confidence=Confidence.HIGH,
        summary=(
            "A low-level call destination could not be resolved statically. ArcAudit could not "
            "exclude a runtime dependency on Ethereum's omitted beacon-roots address."
        ),
        evidence=(
            Evidence(
                evidence_type=EvidenceType.NOT_CHECKED,
                summary="Destination data flow exceeds constant-only resolution.",
                source=f"{source_path}:{source_line}" if source_line is not None else source_path,
                metadata={
                    "source_path": source_path,
                    "source_lines": source_lines,
                    "contract": contract_name,
                    "function": function_name,
                    "call_kind": call_kind,
                    "profile_id": profile.profile_id,
                    "profile_revision": profile.revision,
                },
            ),
        ),
        source_urls=(_SOURCE_URL,),
    )
