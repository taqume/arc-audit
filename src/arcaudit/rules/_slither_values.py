"""Conservative constant resolution shared by Slither-backed rules."""

from __future__ import annotations

from slither.core.expressions.literal import Literal
from slither.core.expressions.type_conversion import TypeConversion as TypeConversionExpression
from slither.core.variables.state_variable import StateVariable
from slither.slithir.operations import Operation, TypeConversion
from slither.slithir.variables.constant import Constant


def resolve_constant_int(value: object, operations: list[Operation]) -> int | None:
    """Resolve only literal and direct-conversion integer values in one IR node."""

    if isinstance(value, Constant):
        return _integer_value(value.value)
    if isinstance(value, StateVariable) and value.is_constant:
        return _constant_expression_int(value.expression)
    for operation in operations:
        if not isinstance(operation, TypeConversion) or operation.lvalue is not value:
            continue
        if isinstance(operation.variable, Constant):
            return _integer_value(operation.variable.value)
    return None


def _constant_expression_int(expression: object) -> int | None:
    """Peel literal-only Solidity type conversions from constant expressions."""

    if isinstance(expression, Literal):
        return _integer_value(expression.value)
    if isinstance(expression, TypeConversionExpression):
        return _constant_expression_int(expression.expression)
    return None


def _integer_value(value: object) -> int | None:
    """Normalize Slither integer literals without evaluating expressions."""

    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return None
    try:
        return int(value, 16 if value.lower().startswith("0x") else 10)
    except ValueError:
        return None
