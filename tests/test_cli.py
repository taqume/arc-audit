from __future__ import annotations

import json

from arcaudit.cli import main


def test_profile_show_json(capsys: object) -> None:
    exit_code = main(["profile", "show", "arc-testnet", "--format", "json"])

    assert exit_code == 0
    captured = capsys.readouterr()  # type: ignore[attr-defined]
    payload = json.loads(captured.out)
    assert payload["profile_id"] == "arc-testnet"
    assert payload["chain_id"] == 5_042_002
