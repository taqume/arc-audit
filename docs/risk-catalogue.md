# ArcAudit risk catalogue

This catalogue is an implementation queue, not a list of confirmed vulnerabilities. Every candidate requires a versioned Arc premise, baseline-tool comparison, fixtures, applicability rules, and a false-positive review.

| Candidate | Family | Arc-specific premise | Likely engine | Initial status |
| --- | --- | --- | --- | --- |
| `native-erc20-amount-domain` | USDC amounts | One balance is exposed through 18-decimal native and 6-decimal ERC-20 domains | Solidity semantic analysis | Spike |
| `eip7708-native-stream-omitted` | Indexing | Plain native USDC sends appear only in the system event stream | TypeScript integration analysis | Candidate |
| `eip7708-double-credit-path` | Indexing | ERC-20 interaction can produce system and ERC-20 logs for one movement | Offchain data-flow analysis | Research |
| `eip7708-historical-boundary` | Indexing | Testnet event shape and emitter changed at the Zero5 boundary | Configuration and index-range analysis | Candidate |
| `prevrandao-security-sink` | Randomness | `PREVRANDAO` returns zero on supported Arc profiles | Solidity source-to-sink analysis | Spike; overlaps ArcReady broadly |
| [`ARC-EVM-001`](rules/ARC-EVM-001.md) `beacon-root-assumption` | Randomness | Ethereum beacon-root behavior is unavailable on Arc | Slither IR semantic analysis | Implemented in `0.1.0.dev0` |
| [`ARC-EVM-002`](rules/ARC-EVM-002.md) `blob-opcode-assumption` | EVM compatibility | Blob transactions are unsupported and blob opcodes have Arc-specific values | Slither IR semantic analysis | Implemented in `0.1.0.dev0` |
| [`ARC-VALUE-001`](rules/ARC-VALUE-001.md) `restricted-native-value-target` | Native value | Arc rejects selected nonzero native-value destinations | Slither IR plus profile addresses | Implemented in `0.1.0.dev0` |
| `arc-selfdestruct-beneficiary` | Native value | Arc combines EIP-6780 with additional native-balance beneficiary rules | Solidity semantic analysis plus scenarios | Candidate |
| `strict-timestamp-ordering` | Ordering | Sub-second blocks may share a timestamp | Sink-aware source/integration analysis | Research; broad matching rejected |
| `excess-confirmation-policy` | Finality | Additional confirmations do not add reorg security after deterministic finality | Integration/configuration analysis | Reuse or extend ArcReady |
| `callfrom-integration-guardrails` | Transaction extensions | Memo and Multicall3From preserve the original EOA through CallFrom with named constraints | Solidity and TypeScript integration analysis | Candidate |
| `empty-account-drain` | Account state | A documented Testnet limitation affects a specific new-account meta-transaction flow | Doctor/probe | Research; profile-bound |

Canonical technical evidence currently lives in `research/arc-master-prompt-audit.md`. Implemented rules will receive stable documents under `rules/`.
