# ARC-EVM-001: Ethereum beacon-roots contract dependency

## Summary

Arc omits Ethereum's EIP-4788 beacon-roots contract. A contract that directly calls Ethereum's canonical beacon-roots address receives empty data on Arc and may revert, decode invalid data, or make an incorrect protocol decision.

Arc source: [Execution and opcode differences](https://docs.arc.io/arc/references/evm-differences#execution-and-opcode-differences).

## Classification

| Field | Value |
| --- | --- |
| Category | Compatibility |
| Default severity | Medium |
| Confidence | High for a resolved literal destination |
| Engine | Slither IR |
| Rule version | `1.0.0` |

The default severity does not assume that the returned value reaches a security-sensitive sink. A later sink-aware rule may raise a separate security finding when stronger evidence exists.

## Detection boundary

The first implementation reports a finding when a low-level call destination resolves to Ethereum's canonical EIP-4788 address through either:

- a constant state variable initialized with the address; or
- a direct `address(...)` conversion at the call site.

Declaring the address without calling it does not produce a finding. A call through a runtime-configurable address produces `UNKNOWN` because ArcAudit cannot exclude the omitted beacon-roots address at runtime.

## Evidence and coverage

The result includes the source path and lines, contract and function names, low-level call kind, selected Arc profile revision, normalized destination, and official Arc source URL.

Fixtures:

- `lab/beacon-root-assumption/src/VulnerableBeaconRootConsumer.sol`
- `lab/beacon-root-assumption/direct-literal/`
- `lab/beacon-root-assumption/safe/`
- `lab/beacon-root-assumption-unknown/`

## Existing-tool comparison

Slither supplies the compilation, CFG, and IR foundation but does not ship this Arc profile rule. ArcReady covers selected Arc compatibility patterns, including `PREVRANDAO` and blob transaction submissions; its reviewed rule catalogue did not contain this beacon-roots call rule when `ARC-EVM-001` was introduced.

## Remediation

Remove the Ethereum beacon-roots dependency for Arc deployments. Use an Arc-supported oracle or another explicitly designed, authenticated source appropriate to the application's trust model. Do not treat `parentBeaconBlockRoot` as an equivalent randomness source on Arc.
