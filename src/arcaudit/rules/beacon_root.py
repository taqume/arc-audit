"""Detect direct dependencies on Ethereum's omitted EIP-4788 beacon-roots contract."""

from __future__ import annotations

from slither.core.expressions.literal import Literal
from slither.core.variables.state_variable import StateVariable
from slither.slither import Slither
from slither.slithir.operations import LowLevelCall, Operation, TypeConversion
from slither.slithir.variables.constant import Constant

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

_RULE_ID = "ARC-EVM-001"
_RULE_VERSION = "1.0.0"
_ETHEREUM_BEACON_ROOTS = int("000F3df6D732807Ef1319fB7B8bB8522d0Beac02", 16)
_SOURCE_URL = "https://docs.arc.io/arc/references/evm-differences#execution-and-opcode-differences"


def evaluate_beacon_root_assumption(
    slither: Slither, profile: NetworkProfile
) -> tuple[CheckResult, ...]:
    """Find low-level calls to the Ethereum EIP-4788 system-contract address."""

    results: list[CheckResult] = []
    for contract in slither.contracts:
        for function in contract.functions_and_modifiers:
            for node in function.nodes:
                for operation in node.irs:
                    if not isinstance(operation, LowLevelCall):
                        continue
                    resolved_address = _resolved_address(operation.destination, node.irs)
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

    if results:
        return tuple(results)
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


def _resolved_address(destination: object, operations: list[Operation]) -> int | None:
    """Resolve the first high-confidence destination shape supported by this rule."""

    if isinstance(destination, StateVariable) and destination.is_constant:
        expression = destination.expression
        if isinstance(expression, Literal):
            return _address_value(expression.value)

    for operation in operations:
        if not isinstance(operation, TypeConversion) or operation.lvalue is not destination:
            continue
        if isinstance(operation.variable, Constant):
            return _address_value(operation.variable.value)
    return None


def _address_value(value: object) -> int | None:
    """Normalize Slither literal values without accepting arbitrary expressions."""

    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return None
    try:
        return int(value, 16)
    except ValueError:
        return None
