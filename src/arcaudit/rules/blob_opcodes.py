"""Detect dependencies on Arc's constant blob-opcode return values."""

from __future__ import annotations

from pathlib import Path

from slither.core.declarations.solidity_variables import SolidityVariableComposed
from slither.slither import Slither
from slither.slithir.operations import Operation, SolidityCall

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
from arcaudit.rules._slither_scope import iter_target_contracts, source_is_in_target

_RULE_ID = "ARC-EVM-002"
_RULE_VERSION = "1.0.0"
_SOURCE_URL = "https://docs.arc.io/arc/references/evm-differences#execution-and-opcode-differences"
_ARC_BEHAVIOR = {
    "BLOBHASH": "always returns 0 because Arc does not support blob transactions",
    "BLOBBASEFEE": "always returns 1 because Arc does not support blob transactions",
}


def evaluate_blob_opcode_assumptions(
    slither: Slither, profile: NetworkProfile, target_files: frozenset[Path]
) -> tuple[CheckResult, ...]:
    """Find Solidity IR that reads BLOBHASH or BLOBBASEFEE on Arc."""

    results: list[CheckResult] = []
    seen_locations: set[tuple[str, tuple[int, ...], str]] = set()
    for contract in iter_target_contracts(slither, target_files):
        for function in contract.functions_and_modifiers:
            for node in function.nodes:
                if not source_is_in_target(node.source_mapping, target_files):
                    continue
                for operation in node.irs:
                    opcode = _blob_opcode(operation)
                    if opcode is None:
                        continue
                    source = node.source_mapping
                    location = (source.filename.short, tuple(source.lines), opcode)
                    if location in seen_locations:
                        continue
                    seen_locations.add(location)
                    source_line = source.lines[0] if source.lines else None
                    results.append(
                        CheckResult(
                            check_id=_RULE_ID,
                            check_version=_RULE_VERSION,
                            title=f"Arc {opcode} constant-value dependency",
                            outcome=Outcome.FINDING,
                            applicability=Applicability.APPLICABLE,
                            severity=Severity.MEDIUM,
                            confidence=Confidence.HIGH,
                            summary=(
                                f"The contract reads {opcode}, which {_ARC_BEHAVIOR[opcode]}. "
                                "Code that expects Ethereum blob semantics can make an incorrect "
                                "protocol or pricing decision."
                            ),
                            evidence=(
                                Evidence(
                                    evidence_type=EvidenceType.STATIC_PROVEN,
                                    summary=f"Slither resolved a direct {opcode} read.",
                                    observed=opcode,
                                    expected="no dependency on Ethereum blob opcode semantics",
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
                                        "arc_behavior": _ARC_BEHAVIOR[opcode],
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
            title="Arc blob opcode dependency",
            outcome=Outcome.PASS,
            applicability=Applicability.APPLICABLE,
            confidence=Confidence.HIGH,
            summary="No BLOBHASH or BLOBBASEFEE read was present in the analyzed Slither IR.",
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


def _blob_opcode(operation: Operation) -> str | None:
    """Map supported Slither IR shapes to their underlying blob opcode."""

    if isinstance(operation, SolidityCall) and operation.function.name == "blobhash(uint256)":
        return "BLOBHASH"
    if any(
        isinstance(value, SolidityVariableComposed) and value.name == "block.blobbasefee"
        for value in operation.read
    ):
        return "BLOBBASEFEE"
    return None
