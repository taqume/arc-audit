# ArcAudit rules

Each promoted rule has a stable identifier and documents its Arc premise, detection boundary, evidence, false-positive controls, baseline-tool overlap, fixtures, and remediation.

| Rule | Status | Summary |
| --- | --- | --- |
| [`ARC-EVM-001`](ARC-EVM-001.md) | Pre-release | Detect direct low-level calls to Ethereum's omitted EIP-4788 beacon-roots contract |
| [`ARC-EVM-002`](ARC-EVM-002.md) | Pre-release | Detect Solidity dependencies on Arc's constant blob opcode values |
| [`ARC-VALUE-001`](ARC-VALUE-001.md) | Pre-release | Detect proven nonzero native-value transfers to Arc-forbidden targets |
