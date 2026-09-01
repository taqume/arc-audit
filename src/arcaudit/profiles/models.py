"""Typed representation of reviewed Arc network profile data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from arcaudit.domain.models import JsonValue


@dataclass(frozen=True, slots=True)
class NativeCurrency:
    """Native currency metadata for a network profile."""

    name: str
    symbol: str
    decimals: int

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> NativeCurrency:
        """Validate and construct native-currency metadata."""

        decimals = int(value["decimals"])
        if decimals < 0:
            raise ValueError("native currency decimals cannot be negative")
        return cls(name=str(value["name"]), symbol=str(value["symbol"]), decimals=decimals)

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation."""

        return {"name": self.name, "symbol": self.symbol, "decimals": self.decimals}


@dataclass(frozen=True, slots=True)
class RpcProfile:
    """Reviewed public RPC endpoints for a network."""

    http: str
    websocket: str | None

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> RpcProfile:
        """Construct RPC metadata without contacting the endpoint."""

        return cls(http=str(value["http"]), websocket=_optional_str(value.get("websocket")))

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation."""

        return {"http": self.http, "websocket": self.websocket}


@dataclass(frozen=True, slots=True)
class ExplorerProfile:
    """Explorer and source-verification metadata."""

    base_url: str
    verifier_kind: str
    verifier_api: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ExplorerProfile:
        """Construct explorer metadata."""

        return cls(
            base_url=str(value["base_url"]),
            verifier_kind=str(value["verifier_kind"]),
            verifier_api=str(value["verifier_api"]),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation."""

        return {
            "base_url": self.base_url,
            "verifier_kind": self.verifier_kind,
            "verifier_api": self.verifier_api,
        }


@dataclass(frozen=True, slots=True)
class ProtocolActivation:
    """A protocol boundary interpreted against an observed block timestamp."""

    activation_id: str
    effective_at: str
    source_urls: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> ProtocolActivation:
        """Construct a protocol activation boundary."""

        return cls(
            activation_id=str(value["id"]),
            effective_at=str(value["effective_at"]),
            source_urls=tuple(str(url) for url in value.get("source_urls", [])),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation."""

        return {
            "id": self.activation_id,
            "effective_at": self.effective_at,
            "source_urls": list(self.source_urls),
        }


@dataclass(frozen=True, slots=True)
class AddressRecord:
    """A network-scoped address with ownership and feature provenance."""

    record_id: str
    address: str
    kind: str
    managed_by: str
    protocol_feature: str | None
    source_url: str

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> AddressRecord:
        """Validate and construct a profile address record."""

        address = str(value["address"])
        if not _is_evm_address(address):
            raise ValueError(f"invalid EVM address for {value.get('id', '<unknown>')}: {address}")
        return cls(
            record_id=str(value["id"]),
            address=address,
            kind=str(value["kind"]),
            managed_by=str(value["managed_by"]),
            protocol_feature=_optional_str(value.get("protocol_feature")),
            source_url=str(value["source_url"]),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a JSON-compatible representation."""

        return {
            "id": self.record_id,
            "address": self.address,
            "kind": self.kind,
            "managed_by": self.managed_by,
            "protocol_feature": self.protocol_feature,
            "source_url": self.source_url,
        }


@dataclass(frozen=True, slots=True)
class NetworkProfile:
    """Reviewed, immutable network facts used by checks and probes."""

    profile_id: str
    revision: str
    network_name: str
    chain_id: int
    deployment_phase: str
    evm_baseline: str
    verified_at: str
    native_currency: NativeCurrency
    rpc: RpcProfile
    explorer: ExplorerProfile
    product_identifiers: dict[str, JsonValue]
    protocol_activations: tuple[ProtocolActivation, ...]
    addresses: tuple[AddressRecord, ...]
    features: dict[str, JsonValue]
    source_urls: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> NetworkProfile:
        """Validate a serialized profile at the package boundary."""

        chain_id = int(value["chain_id"])
        if chain_id <= 0:
            raise ValueError("chain_id must be positive")

        addresses = tuple(AddressRecord.from_dict(item) for item in value["addresses"])
        record_ids = [record.record_id for record in addresses]
        if len(record_ids) != len(set(record_ids)):
            raise ValueError("profile address ids must be unique")

        return cls(
            profile_id=str(value["profile_id"]),
            revision=str(value["revision"]),
            network_name=str(value["network_name"]),
            chain_id=chain_id,
            deployment_phase=str(value["deployment_phase"]),
            evm_baseline=str(value["evm_baseline"]),
            verified_at=str(value["verified_at"]),
            native_currency=NativeCurrency.from_dict(value["native_currency"]),
            rpc=RpcProfile.from_dict(value["rpc"]),
            explorer=ExplorerProfile.from_dict(value["explorer"]),
            product_identifiers=dict(value.get("product_identifiers", {})),
            protocol_activations=tuple(
                ProtocolActivation.from_dict(item) for item in value.get("protocol_activations", [])
            ),
            addresses=addresses,
            features=dict(value.get("features", {})),
            source_urls=tuple(str(url) for url in value.get("source_urls", [])),
        )

    def address(self, record_id: str) -> AddressRecord:
        """Resolve a named address without exposing storage layout to rules."""

        for record in self.addresses:
            if record.record_id == record_id:
                return record
        raise KeyError(f"address record not found: {record_id}")

    def to_dict(self) -> dict[str, JsonValue]:
        """Return the complete profile as versioned JSON data."""

        return {
            "profile_id": self.profile_id,
            "revision": self.revision,
            "network_name": self.network_name,
            "chain_id": self.chain_id,
            "deployment_phase": self.deployment_phase,
            "evm_baseline": self.evm_baseline,
            "verified_at": self.verified_at,
            "native_currency": self.native_currency.to_dict(),
            "rpc": self.rpc.to_dict(),
            "explorer": self.explorer.to_dict(),
            "product_identifiers": dict(self.product_identifiers),
            "protocol_activations": [item.to_dict() for item in self.protocol_activations],
            "addresses": [item.to_dict() for item in self.addresses],
            "features": dict(self.features),
            "source_urls": list(self.source_urls),
        }


def _optional_str(value: object) -> str | None:
    """Normalize optional serialized strings."""

    return None if value is None else str(value)


def _is_evm_address(value: str) -> bool:
    """Validate address shape while allowing either checksum casing."""

    if len(value) != 42 or not value.startswith("0x"):
        return False
    try:
        int(value[2:], 16)
    except ValueError:
        return False
    return True
