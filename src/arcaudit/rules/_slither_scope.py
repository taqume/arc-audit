"""Shared source-boundary helpers for Slither-backed rules."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from slither.core.declarations.contract import Contract
from slither.core.source_mapping.source_mapping import Source
from slither.slither import Slither


def iter_target_contracts(slither: Slither, target_files: frozenset[Path]) -> Iterator[Contract]:
    """Yield contracts declared in the explicit project-source boundary."""

    for contract in slither.contracts:
        source_path = Path(contract.source_mapping.filename.absolute).resolve()
        if source_path in target_files:
            yield contract


def source_is_in_target(source: Source, target_files: frozenset[Path]) -> bool:
    """Return whether one IR node originates from a target project source file."""

    return Path(source.filename.absolute).resolve() in target_files
