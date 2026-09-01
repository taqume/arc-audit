# Changelog

All notable changes to ArcAudit will be documented in this file.

## Unreleased

### Added

- Initial project, documentation, and development-environment foundation.
- Shared outcome, severity, confidence, applicability, evidence, coverage, and report models.
- Versioned Arc Testnet profile loading with product-specific identifiers and address provenance.
- Offline Foundry and Hardhat project discovery.
- Read-only Arc chain, latest-block, and `PREVRANDAO` JSON-RPC probes.
- Text and versioned JSON report adapters plus the initial `arcaudit` CLI.
- Slither-backed `ARC-EVM-001` detection for direct dependencies on Ethereum's omitted EIP-4788 beacon-roots contract.
- Explicit `--allow-build` permission before semantic analysis invokes a target project's compiler framework.
