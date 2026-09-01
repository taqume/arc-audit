"""Read-only Arc JSON-RPC conformance probes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

from arcaudit.domain import (
    Applicability,
    CheckResult,
    Confidence,
    Coverage,
    Evidence,
    EvidenceType,
    NetworkObservation,
    Outcome,
    Report,
    Severity,
)
from arcaudit.domain.models import JsonValue
from arcaudit.profiles.models import NetworkProfile
from arcaudit.version import __version__

_PREVRANDAO_RETURN_CREATION_CODE = "0x4460005260206000f3"


class RpcTransport(Protocol):
    """Minimal transport boundary used by deterministic probe tests."""

    endpoint: str

    def call(self, method: str, params: list[JsonValue]) -> JsonValue:
        """Execute one read-only JSON-RPC request."""

        ...


class RpcRequestError(RuntimeError):
    """Raised when an RPC request cannot provide a usable result."""


@dataclass(slots=True)
class UrllibRpcTransport:
    """Dependency-free HTTP transport for Arc read-only JSON-RPC calls."""

    endpoint: str
    timeout_seconds: float = 10.0
    _request_id: int = 0

    def __post_init__(self) -> None:
        """Reject non-HTTP transports before any network request is made."""

        if urlsplit(self.endpoint).scheme not in {"http", "https"}:
            raise ValueError("RPC endpoint must use http or https")

    def call(self, method: str, params: list[JsonValue]) -> JsonValue:
        """Execute a JSON-RPC request without logging endpoint credentials."""

        self._request_id += 1
        payload = json.dumps(
            {"jsonrpc": "2.0", "id": self._request_id, "method": method, "params": params}
        ).encode("utf-8")
        request = Request(
            self.endpoint,
            data=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": f"ArcAudit/{__version__}",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise RpcRequestError(f"RPC HTTP request failed (status={error.code})") from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise RpcRequestError(f"RPC transport failed: {type(error).__name__}") from error

        if not isinstance(body, dict):
            raise RpcRequestError("RPC response must be a JSON object")
        if "error" in body:
            rpc_error_payload = body["error"]
            code = rpc_error_payload.get("code") if isinstance(rpc_error_payload, dict) else None
            raise RpcRequestError(f"RPC returned an error response (code={code})")
        if "result" not in body:
            raise RpcRequestError("RPC response did not include a result")
        return cast(JsonValue, body["result"])


def probe_network(
    profile: NetworkProfile,
    *,
    rpc_url: str | None = None,
    transport: RpcTransport | None = None,
) -> Report:
    """Verify network identity and selected Arc behavior using read-only calls."""

    active_transport = transport or UrllibRpcTransport(rpc_url or profile.rpc.http)
    endpoint = _redact_endpoint(active_transport.endpoint)
    results: list[CheckResult] = []
    chain_id: int | None = None
    block_number: int | None = None
    block_timestamp: int | None = None

    try:
        chain_id = _parse_hex_quantity(active_transport.call("eth_chainId", []))
        matches = chain_id == profile.chain_id
        results.append(
            CheckResult(
                check_id="ARCAUDIT-PROBE-CHAIN-001",
                check_version="1.0.0",
                title="Arc network identity",
                outcome=Outcome.PASS if matches else Outcome.FINDING,
                applicability=Applicability.APPLICABLE,
                severity=None if matches else Severity.HIGH,
                confidence=Confidence.HIGH,
                summary=(
                    f"RPC chain ID matches {profile.profile_id}."
                    if matches
                    else f"RPC chain ID {chain_id} does not match profile chain {profile.chain_id}."
                ),
                evidence=(
                    Evidence(
                        evidence_type=EvidenceType.RPC_OBSERVED,
                        summary="Observed eth_chainId from the configured endpoint.",
                        observed=chain_id,
                        expected=profile.chain_id,
                        metadata={"endpoint": endpoint, "profile_revision": profile.revision},
                    ),
                ),
                source_urls=profile.source_urls,
            )
        )
    except (RpcRequestError, TypeError, ValueError) as error:
        results.append(_rpc_error_result("ARCAUDIT-PROBE-CHAIN-001", "Arc network identity", error))

    try:
        raw_block = active_transport.call("eth_getBlockByNumber", ["latest", False])
        if not isinstance(raw_block, dict):
            raise RpcRequestError("latest block result must be an object")
        block_number = _parse_hex_quantity(raw_block.get("number"))
        block_timestamp = _parse_hex_quantity(raw_block.get("timestamp"))
        results.append(
            CheckResult(
                check_id="ARCAUDIT-PROBE-BLOCK-001",
                check_version="1.0.0",
                title="Latest block evidence",
                outcome=Outcome.PASS,
                applicability=Applicability.APPLICABLE,
                confidence=Confidence.HIGH,
                summary=f"Captured latest block {block_number} for profile-bound evidence.",
                evidence=(
                    Evidence(
                        evidence_type=EvidenceType.RPC_OBSERVED,
                        summary="Observed latest block number and timestamp.",
                        observed={"number": block_number, "timestamp": block_timestamp},
                        expected="a valid latest block",
                        metadata={"endpoint": endpoint},
                    ),
                ),
            )
        )
    except (RpcRequestError, TypeError, ValueError) as error:
        results.append(
            _rpc_error_result("ARCAUDIT-PROBE-BLOCK-001", "Latest block evidence", error)
        )

    try:
        raw_prevrandao = active_transport.call(
            "eth_call", [{"data": _PREVRANDAO_RETURN_CREATION_CODE}, "latest"]
        )
        prevrandao = _parse_hex_quantity(raw_prevrandao)
        matches = prevrandao == 0
        results.append(
            CheckResult(
                check_id="ARCAUDIT-PROBE-PREVRANDAO-001",
                check_version="1.0.0",
                title="Arc PREVRANDAO behavior",
                outcome=Outcome.PASS if matches else Outcome.FINDING,
                applicability=Applicability.APPLICABLE,
                severity=None if matches else Severity.MEDIUM,
                confidence=Confidence.HIGH,
                summary=(
                    "PREVRANDAO returned the profile-defined constant zero."
                    if matches
                    else f"PREVRANDAO returned {prevrandao}; the reviewed profile expects zero."
                ),
                evidence=(
                    Evidence(
                        evidence_type=EvidenceType.RPC_OBSERVED,
                        summary="Executed creation-form bytecode that returns PREVRANDAO.",
                        observed=prevrandao,
                        expected=0,
                        metadata={
                            "endpoint": endpoint,
                            "creation_code": _PREVRANDAO_RETURN_CREATION_CODE,
                            "profile_revision": profile.revision,
                        },
                    ),
                ),
                source_urls=(
                    "https://docs.arc.io/arc/references/evm-differences#execution-and-opcode-differences",
                ),
            )
        )
    except (RpcRequestError, TypeError, ValueError) as error:
        results.append(
            _rpc_error_result("ARCAUDIT-PROBE-PREVRANDAO-001", "Arc PREVRANDAO behavior", error)
        )

    return Report.create(
        tool_version=__version__,
        command="probe",
        target=endpoint,
        results=tuple(results),
        coverage=Coverage(files_considered=0, files_analyzed=0, analyzers=("arc-json-rpc",)),
        network=NetworkObservation(
            profile_id=profile.profile_id,
            profile_revision=profile.revision,
            endpoint=endpoint,
            chain_id=chain_id,
            block_number=block_number,
            block_timestamp=block_timestamp,
        ),
    )


def _parse_hex_quantity(value: JsonValue) -> int:
    """Parse an Ethereum JSON-RPC quantity and reject ambiguous representations."""

    if not isinstance(value, str) or not value.startswith("0x"):
        raise TypeError("RPC quantity must be a 0x-prefixed string")
    return int(value, 16)


def _redact_endpoint(endpoint: str) -> str:
    """Remove credentials and query parameters before storing endpoint evidence."""

    parts = urlsplit(endpoint)
    host = parts.hostname or ""
    if parts.port is not None:
        host = f"{host}:{parts.port}"
    return urlunsplit((parts.scheme, host, parts.path, "", ""))


def _rpc_error_result(check_id: str, title: str, error: Exception) -> CheckResult:
    """Convert infrastructure failure into an explicit ERROR outcome."""

    return CheckResult(
        check_id=check_id,
        check_version="1.0.0",
        title=title,
        outcome=Outcome.ERROR,
        applicability=Applicability.UNKNOWN,
        confidence=Confidence.HIGH,
        summary=str(error),
        evidence=(
            Evidence(
                evidence_type=EvidenceType.NOT_CHECKED,
                summary="The read-only RPC check could not establish evidence.",
            ),
        ),
    )
