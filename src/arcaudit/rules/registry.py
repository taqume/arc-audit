"""Single registry for Slither-backed ArcAudit rule execution and coverage."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from slither.slither import Slither

from arcaudit.domain import CheckResult
from arcaudit.profiles.models import NetworkProfile
from arcaudit.rules.beacon_root import evaluate_beacon_root_assumption
from arcaudit.rules.blob_opcodes import evaluate_blob_opcode_assumptions
from arcaudit.rules.native_value import evaluate_native_value_targets
from arcaudit.rules.selfdestruct import evaluate_selfdestruct_beneficiaries

RuleEvaluator = Callable[[Slither, NetworkProfile], tuple[CheckResult, ...]]


@dataclass(frozen=True, slots=True)
class RuleDefinition:
    """Bind one stable rule identifier to its semantic evaluator."""

    rule_id: str
    evaluate: RuleEvaluator


SLITHER_RULES = (
    RuleDefinition("ARC-EVM-001", evaluate_beacon_root_assumption),
    RuleDefinition("ARC-EVM-002", evaluate_blob_opcode_assumptions),
    RuleDefinition("ARC-VALUE-001", evaluate_native_value_targets),
    RuleDefinition("ARC-SELFDESTRUCT-001", evaluate_selfdestruct_beneficiaries),
)
