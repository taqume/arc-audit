"""Load reviewed profiles bundled with ArcAudit."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

from arcaudit.profiles.models import NetworkProfile

_PROFILE_FILES = {"arc-testnet": "arc-testnet.json"}


class ProfileNotFoundError(ValueError):
    """Raised when a requested profile is not bundled with ArcAudit."""


def load_profile(profile_id: str) -> NetworkProfile:
    """Load and validate a bundled network profile by its stable identifier."""

    filename = _PROFILE_FILES.get(profile_id)
    if filename is None:
        supported = ", ".join(sorted(_PROFILE_FILES))
        raise ProfileNotFoundError(f"unknown profile '{profile_id}'; supported: {supported}")

    profile_file = files("arcaudit.profiles.data").joinpath(filename)
    raw: dict[str, Any] = json.loads(profile_file.read_text(encoding="utf-8"))
    profile = NetworkProfile.from_dict(raw)
    if profile.profile_id != profile_id:
        raise ValueError(
            f"profile id mismatch: requested '{profile_id}', loaded '{profile.profile_id}'"
        )
    return profile
