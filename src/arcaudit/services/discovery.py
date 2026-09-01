"""Bounded, non-executing project discovery helpers."""

from __future__ import annotations

import os
from pathlib import Path

_IGNORED_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "broadcast",
    "build",
    "cache",
    "dist",
    "lib",
    "node_modules",
    "out",
    "script",
    "scripts",
    "test",
    "tests",
    "vendor",
}


def discover_files(
    root: Path, suffixes: tuple[str, ...], *, limit: int = 10_000
) -> tuple[Path, ...]:
    """Find relevant files without following symlinks or entering generated directories."""

    discovered: list[Path] = []
    for current_root, directory_names, file_names in os.walk(root, followlinks=False):
        directory_names[:] = sorted(
            name for name in directory_names if name not in _IGNORED_DIRECTORIES
        )
        current = Path(current_root)
        for file_name in sorted(file_names):
            if not file_name.endswith(suffixes):
                continue
            discovered.append(current / file_name)
            if len(discovered) >= limit:
                return tuple(discovered)
    return tuple(discovered)
