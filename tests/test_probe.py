from __future__ import annotations

from dataclasses import dataclass
from typing import Self
from urllib.request import Request

import pytest

from arcaudit.domain import Outcome
from arcaudit.domain.models import JsonValue
from arcaudit.profiles import load_profile
from arcaudit.services.probe import UrllibRpcTransport, probe_network


@dataclass
class FakeTransport:
    endpoint: str
    responses: dict[str, JsonValue]

    def call(self, method: str, params: list[JsonValue]) -> JsonValue:
        del params
        return self.responses[method]


class FakeHttpResponse:
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        del args

    def read(self) -> bytes:
        return b'{"jsonrpc":"2.0","id":1,"result":"0x4cef52"}'


def test_http_transport_identifies_arcaudit_to_rpc_gateway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str | float] = {}

    def fake_urlopen(request: Request, timeout: float) -> FakeHttpResponse:
        captured["user_agent"] = request.get_header("User-agent", "")
        captured["timeout"] = timeout
        return FakeHttpResponse()

    monkeypatch.setattr("arcaudit.services.probe.urlopen", fake_urlopen)
    transport = UrllibRpcTransport("https://example.test", timeout_seconds=3.0)

    result = transport.call("eth_chainId", [])

    assert result == "0x4cef52"
    assert captured == {"user_agent": "ArcAudit/0.1.0", "timeout": 3.0}


def test_probe_records_chain_block_and_prevrandao_evidence() -> None:
    transport = FakeTransport(
        endpoint="https://user:secret@example.test/rpc?api_key=hidden",
        responses={
            "eth_chainId": "0x4cef52",
            "eth_getBlockByNumber": {"number": "0x10", "timestamp": "0x20"},
            "eth_call": "0x" + ("00" * 32),
        },
    )

    report = probe_network(load_profile("arc-testnet"), transport=transport)

    assert [result.outcome for result in report.results] == [
        Outcome.PASS,
        Outcome.PASS,
        Outcome.PASS,
    ]
    assert report.network is not None
    assert report.network.chain_id == 5_042_002
    assert report.network.block_number == 16
    assert report.network.endpoint == "https://example.test/rpc"


def test_probe_reports_profile_mismatch_as_finding() -> None:
    transport = FakeTransport(
        endpoint="https://example.test",
        responses={
            "eth_chainId": "0x1",
            "eth_getBlockByNumber": {"number": "0x10", "timestamp": "0x20"},
            "eth_call": "0x" + ("00" * 32),
        },
    )

    report = probe_network(load_profile("arc-testnet"), transport=transport)

    assert report.results[0].outcome is Outcome.FINDING
    assert report.results[0].severity is not None
