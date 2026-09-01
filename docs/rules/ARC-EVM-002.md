# ARC-EVM-002: Arc blob opcode dependency

## Summary

Arc rejects EIP-4844 type-3 blob transactions. Its `BLOBHASH` opcode returns `0`, and `BLOBBASEFEE` returns `1`. Contracts that expect Ethereum blob commitments or fee-market values can therefore make incorrect protocol or pricing decisions on Arc.

Arc source: [Execution and opcode differences](https://docs.arc.io/arc/references/evm-differences#execution-and-opcode-differences).

## Classification

| Field | Value |
| --- | --- |
| Category | Compatibility |
| Default severity | Medium |
| Confidence | High for a resolved opcode read |
| Engine | Slither IR |
| Rule version | `1.0.0` |

The default severity establishes a broken cross-chain assumption without claiming that the value reaches a security-sensitive sink. A future data-flow rule may classify proven financial or authorization impact separately.

## Detection boundary

The first implementation reports each Solidity IR location that:

- invokes the `blobhash(uint256)` builtin; or
- reads `block.blobbasefee`, including reads nested inside expressions.

Externally supplied commitment or fee values do not produce a finding. This rule does not inspect precompiled deployment bytecode, inline Yul that Slither does not lower into the supported IR shapes, or offchain type-3 transaction construction.

## Evidence and coverage

Each result includes the source path and lines, contract and function names, opcode, selected Arc profile revision, Arc runtime behavior, and official Arc source URL. Coverage counts only source files Slither actually compiled, not every Solidity file discovered under the target directory.

Fixtures:

- `lab/blob-opcode-assumption/`
- `lab/blob-opcode-assumption-edge/`
- `lab/blob-opcode-assumption-safe/`

## Existing-tool comparison

Slither supplies compilation and semantic IR but does not ship an Arc blob-opcode rule. ArcReady covers selected ethers and viem type-3 transaction submissions; its reviewed catalogue does not cover the Solidity opcode semantics handled here. Foundry compiles and tests the fixtures but does not flag the Arc incompatibility by itself.

## Remediation

Do not depend on Ethereum blob commitments or blob fee-market values in Arc deployments. Use an Arc-supported data-availability or authenticated commitment source chosen for the application's trust model. Keep offchain transaction builders from submitting type-3 transactions to Arc.
