# ARC-VALUE-001: Arc-forbidden native-value target

## Summary

Arc rejects a nonzero native-value transfer to the zero address or a precompile, even when the sender has sufficient balance. This differs from a standard EVM assumption that a literal low-level destination can receive value as long as the call itself is otherwise valid.

Arc sources: [Value transfer rules](https://docs.arc.io/arc/references/evm-differences#value-transfer-rules) and [protocol precompiles](https://docs.arc.io/arc/concepts/execution-layer#protocol-precompiles).

## Classification

| Field | Value |
| --- | --- |
| Category | Compatibility |
| Default severity | Medium |
| Confidence | High when both target and positive value resolve statically |
| Engine | Slither IR plus Arc profile addresses |
| Rule version | `1.0.0` |

The rule reports a guaranteed Arc revert condition, not every native call that could fail at runtime. The default severity does not assume that the caller mishandles the failure or that the path is security-critical.

## Detection boundary

The first implementation evaluates low-level `call`, Solidity `send`, and Solidity `transfer`. It reports a finding only when:

- the native value resolves to a constant greater than zero; and
- the destination resolves to `address(0)` or one of Arc's five custom precompiles recorded in the selected network profile.

Direct literals and constant state variables with literal type conversions are supported. Zero-value calls and ordinary resolved addresses produce no finding. A positive-value path whose potentially restricted destination cannot be resolved produces `UNKNOWN`; a dynamic amount to a proven restricted target does the same. Standard Ethereum precompiles, blocklisted destinations, and accounts destroyed earlier in the same transaction require additional profile or data-flow evidence and remain outside this version.

## Evidence and coverage

Each finding records the normalized destination, native amount, target kind, call kind, source location, contract and function, selected profile revision, and official sources. Profile revision `2026-09-01.2` introduced the five official Arc custom precompiles and the two native-value revert predicates used by the rule; later revisions retain them.

Fixtures:

- `lab/restricted-native-value-target/`
- `lab/restricted-native-value-target-edge/`
- `lab/restricted-native-value-target-safe/`
- `lab/restricted-native-value-target-unknown/`

## Existing-tool comparison

Slither and Wake can report unchecked low-level return values, but that generic behavior is intentionally outside ArcAudit's ownership. The vulnerable low-level fixture checks its return value; this rule reports the Arc-specific destination and value combination. ArcReady's reviewed rule catalogue did not include this Solidity native-value rule when `ARC-VALUE-001` was introduced. Foundry compiles the fixtures but a standard local EVM cannot reproduce Arc's native-value enforcement.

## Remediation

Do not send native value to the zero address or a precompile. Use zero-value calls for precompile invocation and route intended USDC transfers through an allowed recipient or the documented native-coin interfaces. Handle downstream native-call failures even when a static destination is not restricted.
