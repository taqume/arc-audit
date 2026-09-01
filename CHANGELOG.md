# Changelog

All notable changes to ArcAudit will be documented in this file.

## 0.1.0 - 2026-09-01

### Added

- Initial project, documentation, and development-environment foundation.
- Shared outcome, severity, confidence, applicability, evidence, coverage, and report models.
- Versioned Arc Testnet profile loading with product-specific identifiers and address provenance.
- Arc Testnet profile revision `2026-09-01.2` with all five custom protocol precompiles and native-value revert predicates.
- Arc Testnet profile revision `2026-09-01.3` with the seeded blocklisted test address and explicit `SELFDESTRUCT` behavior facts.
- Offline Foundry and Hardhat project discovery.
- Read-only Arc chain, latest-block, and `PREVRANDAO` JSON-RPC probes.
- Text and versioned JSON report adapters plus the initial `arcaudit` CLI.
- Slither-backed `ARC-EVM-001` detection for direct dependencies on Ethereum's omitted EIP-4788 beacon-roots contract.
- Slither-backed `ARC-EVM-002` detection for `BLOBHASH` and `BLOBBASEFEE` dependencies under Arc's constant opcode behavior.
- Slither-backed `ARC-VALUE-001` detection for proven nonzero transfers to the zero address or Arc custom precompiles.
- Slither-backed `ARC-SELFDESTRUCT-001` beneficiary classification with `UNKNOWN` results for unresolved targets.
- Explicit `--allow-build` permission before semantic analysis invokes a target project's compiler framework.
- Explicit partial-coverage reasons when Slither compiles fewer Solidity files than project discovery found.
- `UNKNOWN` results instead of false passes for unresolved beacon-root and positive native-value destinations.
- Compiler failures now report only the attempted Slither engine, not Arc rules that never executed.
- A single Slither rule registry now drives both execution and coverage identifiers.
- A dependency-scope regression fixture and pinned external smoke validation for first-party Circle Hardhat and Foundry projects.
- Bounded malformed-layout and unsupported-compiler regression fixtures.
- Documented CLI process-status contract for completed, finding, error, and incomplete reports.
- Pinned positive corpus validation against the official `circlefin/arc-node` repository.

### Changed

- Slither rules now evaluate only the explicit production-source boundary while retaining imported dependencies for compilation and semantic resolution.
- Default root-project discovery excludes Foundry dependency, test, and script trees from production coverage.
- `UNKNOWN` and `SKIPPED` reports now return exit code `3` instead of appearing complete to shell automation.
