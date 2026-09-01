"""Conservative constant resolution shared by Slither-backed rules."""

from __future__ import annotations

from slither.core.declarations.solidity_variables import SolidityVariable
from slither.core.expressions.literal import Literal
from slither.core.expressions.type_conversion import TypeConversion as TypeConversionExpression
from slither.core.variables.state_variable import StateVariable
from slither.slithir.operations import Operation, TypeConversion
from slither.slithir.variables.constant import Constant


def resolve_constant_int(value: object, operations: list[Operation]) -> int | None:
    """Resolve only literal and direct-conversion integer values in one IR node."""

    return _resolve_constant_int(value, operations, set())


def _resolve_constant_int(
    value: object, operations: list[Operation], seen_values: set[int]
) -> int | None:
    """Follow literal-only conversion chains without evaluating arbitrary data flow."""

    if isinstance(value, Constant):
        return _integer_value(value.value)
    if isinstance(value, StateVariable) and value.is_constant:
        return _constant_expression_int(value.expression)
    value_identity = id(value)
    if value_identity in seen_values:
        return None
    seen_values.add(value_identity)
    for operation in operations:
        if not isinstance(operation, TypeConversion) or operation.lvalue is not value:
            continue
        return _resolve_constant_int(operation.variable, operations, seen_values)
    return None


def resolve_solidity_name(value: object, operations: list[Operation]) -> str | None:
    """Resolve a Solidity builtin through direct IR type conversions."""

    return _resolve_solidity_name(value, operations, set())


def _resolve_solidity_name(
    value: object, operations: list[Operation], seen_values: set[int]
) -> str | None:
    """Follow conversion-only IR to a Solidity builtin variable."""

    if isinstance(value, SolidityVariable):
        return str(value.name)
    value_identity = id(value)
    if value_identity in seen_values:
        return None
    seen_values.add(value_identity)
    for operation in operations:
        if not isinstance(operation, TypeConversion) or operation.lvalue is not value:
            continue
        return _resolve_solidity_name(operation.variable, operations, seen_values)
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
