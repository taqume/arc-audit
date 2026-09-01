# ArcAudit project context

## Product

ArcAudit is a local-first Arc security, compatibility, and conformance platform. It helps developers and software agents identify selected Arc-specific assumptions, validate project and integration configuration, and collect reproducible evidence from supported Arc networks.

ArcAudit is more than a vulnerability scanner. Its value comes from combining semantic contract analysis, offchain integration checks, version-aware protocol knowledge, and scoped live validation behind one deterministic core.

## Users and interfaces

- Contract and application developers use the CLI.
- Python applications and automation use the SDK.
- AI coding agents use the MCP adapter and structured evidence.
- CI systems use JSON, SARIF, policy exit codes, and a GitHub Action.

All interfaces consume the same application services and report schema.

## Product scope

The intended product includes:

- `scan` for Solidity and selected offchain integration analysis;
- `doctor` for offline project checks and read-only network diagnostics;
- `probe` for explicit Arc protocol conformance checks;
- `simulate` for Foundry-backed, reproducible scenarios;
- text, JSON, and eventually SARIF reporting;
- a Python SDK and local-first MCP server;
- a versioned Arc network and hard-fork profile registry;
- an independent vulnerable, safe, and edge-case fixture laboratory.

The product will be delivered in tested milestones. Staged delivery does not reduce the intended final scope.

## Accepted constraints

- Arc Testnet is the first execution profile. Additional profiles require published endpoints, addresses, activation boundaries, and verification evidence.
- ArcReady is a required competitive baseline and a useful MIT-licensed reference. ArcAudit must add deeper or different evidence instead of duplicating its rules without added value.
- Slither is the primary Solidity analysis foundation. ArcAudit will be released as open source under `AGPL-3.0-only`, with required third-party notices preserved.
- Foundry supplies compilation, fixtures, fuzzing, invariants, and scenario execution. ArcAudit will not implement a new EVM.
- Arc and Circle SDKs are optional integration targets, not ArcAudit core dependencies. Static and offline behavior must remain usable without accounts, credentials, Node.js SDKs, or network access.
- Hardhat receives a separate project adapter. Arcscan/Blockscout is an optional read-only evidence source. A full `arc-node` is reserved for advanced or nightly conformance work.
- Anvil and standard forks cannot prove Arc-specific protocol behavior. Reports must identify the execution backend and its limits.
- P2Pass is independent of ArcAudit. It may become a later public usage example, not a release prerequisite or primary test corpus.
- Telemetry is off by default. Source files and secrets stay local unless the user explicitly enables a network operation.
- ArcAudit will ship a local, open-source MCP server. The project does not plan to operate a paid product or hosted MCP service.

## Differentiation target

ArcAudit should differentiate through:

1. source-to-sink Solidity semantics rather than unbounded text matches;
2. Arc native-value and `SELFDESTRUCT` execution rules;
3. EIP-7708 indexing, deduplication, and historical-boundary checks;
4. Memo, Multicall3From, and CallFrom integration checks;
5. evidence-backed live conformance probes that a standard local EVM cannot reproduce;
6. structured findings that both humans and agents can inspect and verify.

## Non-goals

- replacing a professional security audit;
- claiming full security or production readiness from a clean report;
- recreating Slither, Foundry, or a general smart-contract testing framework;
- treating every generic Solidity issue as Arc-specific;
- depending on an LLM to decide whether a vulnerability exists;
- making P2Pass part of the ArcAudit core.

## Current status

The project is implementing the `0.1.0` foundation. The shared report contract, Arc Testnet profile, offline project discovery, and read-only JSON-RPC probe are established. Three Arc-specific Slither rules have passed their initial fixture and baseline-comparison gates; broader corpus measurement and clean-install validation remain before the milestone review.
