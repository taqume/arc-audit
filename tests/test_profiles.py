from __future__ import annotations

import pytest

from arcaudit.profiles import ProfileNotFoundError, load_profile


def test_load_arc_testnet_profile() -> None:
    profile = load_profile("arc-testnet")

    assert profile.chain_id == 5_042_002
    assert profile.native_currency.symbol == "USDC"
    assert profile.native_currency.decimals == 18
    assert profile.product_identifiers["app_kit"] == "Arc_Testnet"
    assert profile.product_identifiers["cctp_domain"] == 26
    assert profile.address("usdc-erc20").address == ("0x3600000000000000000000000000000000000000")
    protocol_precompiles = [
        record for record in profile.addresses if record.kind == "protocol-precompile"
    ]
    assert len(protocol_precompiles) == 5


def test_unknown_profile_is_rejected() -> None:
    with pytest.raises(ProfileNotFoundError, match="unknown profile"):
        load_profile("arc-mainnet")
