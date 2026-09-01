"""Detect SELFDESTRUCT beneficiaries restricted by Arc native-value rules."""

from __future__ import annotations

from slither.core.source_mapping.source_mapping import Source
from slither.slither import Slither
from slither.slithir.operations import SolidityCall

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
from arcaudit.rules._slither_values import resolve_constant_int, resolve_solidity_name

_RULE_ID = "ARC-SELFDESTRUCT-001"
_RULE_VERSION = "1.0.0"
_SOURCE_URLS = (
    "https://docs.arc.io/arc/references/evm-differences#selfdestruct",
    "https://docs.arc.io/arc/concepts/execution-layer#protocol-precompiles",
    "https://docs.arc.io/arc/references/contract-addresses#test-addresses-for-restricted-transfer-behavior",
)


def evaluate_selfdestruct_beneficiaries(
    slither: Slither, profile: NetworkProfile
) -> tuple[CheckResult, ...]:
    """Find statically resolved SELFDESTRUCT beneficiaries that Arc restricts."""

    blocklisted_addresses = {
        int(record.address, 16)
        for record in profile.addresses
        if record.kind == "testnet-blocklisted-address"
    }
    precompiles = {
        int(record.address, 16)
        for record in profile.addresses
        if record.kind == "protocol-precompile"
    }
    results: list[CheckResult] = []
    unresolved_results: list[CheckResult] = []
    for contract in slither.contracts:
        for function in contract.functions_and_modifiers:
            for node in function.nodes:
                for operation in node.irs:
                    if not _is_selfdestruct(operation):
                        continue
                    beneficiary = resolve_constant_int(operation.arguments[0], node.irs)
                    beneficiary_kind = _beneficiary_kind(
                        beneficiary,
                        resolve_solidity_name(operation.arguments[0], node.irs),
                        blocklisted_addresses,
                        precompiles,
                    )
                    if beneficiary_kind is None:
                        if beneficiary is None:
                            unresolved_results.append(
                                _unknown_beneficiary_result(
                                    contract.name,
                                    function.canonical_name,
                                    node.source_mapping,
                                    profile,
                                )
                            )
                        continue
                    if beneficiary_kind == "self":
                        observed = "address(this)"
                    else:
                        assert beneficiary is not None
                        observed = f"0x{beneficiary:040x}"
                    beneficiary_label = {
                        "zero-address": "the zero address",
                        "self": "the contract itself",
                        "blocklisted-test-address": "Arc's seeded blocklisted Testnet address",
                        "arc-precompile": "an Arc precompile",
                    }[beneficiary_kind]
                    source = node.source_mapping
                    source_line = source.lines[0] if source.lines else None
                    results.append(
                        CheckResult(
                            check_id=_RULE_ID,
                            check_version=_RULE_VERSION,
                            title="Arc-restricted SELFDESTRUCT beneficiary",
                            outcome=Outcome.FINDING,
                            applicability=Applicability.APPLICABLE,
                            severity=Severity.MEDIUM,
                            confidence=Confidence.HIGH,
                            summary=(
                                f"SELFDESTRUCT resolves to {beneficiary_label}. On Arc this "
                                "reverts when the contract has a nonzero native USDC balance."
                            ),
                            evidence=(
                                Evidence(
                                    evidence_type=EvidenceType.STATIC_PROVEN,
                                    summary="Slither resolved the SELFDESTRUCT beneficiary.",
                                    observed=observed,
                                    expected="a permitted beneficiary or a proven zero balance",
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
                                        "beneficiary_kind": beneficiary_kind,
                                        "revert_condition": "contract balance is nonzero",
                                        "category": "compatibility",
                                        "profile_id": profile.profile_id,
                                        "profile_revision": profile.revision,
                                    },
                                ),
                            ),
                            source_urls=_SOURCE_URLS,
                        )
                    )

    if results or unresolved_results:
        return (*results, *unresolved_results)
    return (
        CheckResult(
            check_id=_RULE_ID,
            check_version=_RULE_VERSION,
            title="Arc-restricted SELFDESTRUCT beneficiary",
            outcome=Outcome.PASS,
            applicability=Applicability.APPLICABLE,
            confidence=Confidence.HIGH,
            summary=(
                "No SELFDESTRUCT beneficiary resolved to a restricted literal supported by "
                "this rule in the analyzed Slither IR."
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


def _is_selfdestruct(operation: object) -> bool:
    """Recognize Slither's semantic representation of the SELFDESTRUCT opcode."""

    return (
        isinstance(operation, SolidityCall)
        and operation.function.name == "selfdestruct(address)"
        and len(operation.arguments) == 1
    )


def _beneficiary_kind(
    beneficiary: int | None,
    solidity_name: str | None,
    blocklisted_addresses: set[int],
    precompiles: set[int],
) -> str | None:
    """Classify statically provable Arc-restricted beneficiaries."""

    if beneficiary == 0:
        return "zero-address"
    if solidity_name == "this":
        return "self"
    if beneficiary in blocklisted_addresses:
        return "blocklisted-test-address"
    if beneficiary in precompiles:
        return "arc-precompile"
    return None


def _unknown_beneficiary_result(
    contract_name: str, function_name: str, source: Source, profile: NetworkProfile
) -> CheckResult:
    """Represent unresolved beneficiary data flow without producing a false pass."""

    source_lines = list(source.lines)
    source_path = str(source.filename.short)
    source_line = source_lines[0] if source_lines else None
    return CheckResult(
        check_id=_RULE_ID,
        check_version=_RULE_VERSION,
        title="Arc-restricted SELFDESTRUCT beneficiary",
        outcome=Outcome.UNKNOWN,
        applicability=Applicability.UNKNOWN,
        confidence=Confidence.HIGH,
        summary=(
            "SELFDESTRUCT uses a beneficiary that this rule could not resolve statically. "
            "Arc-specific beneficiary restrictions were not established for this path."
        ),
        evidence=(
            Evidence(
                evidence_type=EvidenceType.NOT_CHECKED,
                summary=(
                    "Beneficiary data flow is outside the supported constant-resolution boundary."
                ),
                source=f"{source_path}:{source_line}" if source_line is not None else source_path,
                metadata={
                    "source_path": source_path,
                    "source_lines": source_lines,
                    "contract": contract_name,
                    "function": function_name,
                    "profile_id": profile.profile_id,
                    "profile_revision": profile.revision,
                },
            ),
        ),
        source_urls=_SOURCE_URLS,
    )
