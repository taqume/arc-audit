# ArcAudit delivery roadmap

ArcAudit keeps the full platform vision and delivers it through tested vertical milestones. Version numbers describe usable capability, not throwaway prototypes.

## 0.1.0: foundation and first evidence

Goal: prove that one shared core can produce useful Arc-specific evidence.

- Python package and reproducible `uv` environment;
- AGPL licensing and third-party notices;
- domain models for findings, evidence, coverage, policies, and profiles;
- Arc Testnet profile with dated official sources;
- rule/check registry and application-service boundaries;
- Foundry and Hardhat project discovery without implicit command execution;
- `arcaudit scan`, `arcaudit doctor`, and `arcaudit probe` vertical slices;
- initial rule spikes for beacon-root assumptions, blob-opcode assumptions, restricted native-value targets, and Arc `SELFDESTRUCT` beneficiary semantics;
- at least three high-value Arc-specific automated checks promoted from those spikes through baseline comparison;
- at least one read-only live probe demonstrating behavior a standard local EVM cannot establish;
- optional read-only Arcscan deployment evidence;
- text and versioned JSON reports;
- vulnerable, safe, and edge-case fixtures;
- pytest, Ruff, type checking, package build, and clean-install verification.

The 0.1.0 review must explain each subsystem and report measured false positives, unsupported cases, and remaining coverage.

## 0.2.0: semantic and integration depth

- expand the validated Solidity rule set;
- add TypeScript as the first offchain integration-analysis target;
- add EIP-7708 indexer and named CallFrom integration checks;
- add rule-level documentation and suppression policy;
- add SARIF and CI-friendly policy exit codes;
- benchmark against ArcReady, Slither, and Wake on every overlapping rule family.

## 0.3.0: scenarios and conformance

- Foundry-backed scenario manifests;
- local EVM, forked-state EVM, and Arc Testnet backend labels;
- invariant and regression scenario packs;
- explicit opt-in transaction-producing Testnet probes;
- deterministic evidence capture and redaction tests.

## 0.4.0: public automation interfaces

- stabilize the public Python SDK;
- expose the same application services through a local-first MCP server;
- add bounded agent-oriented schemas and finding explanation resources;
- add SDK/CLI/MCP contract tests to prevent behavioral drift.

## 0.5.0: distribution and CI

- publishable Python package;
- GitHub Action and documented CI recipes;
- container image if it materially improves the Slither/solc/Foundry setup;
- complete installation, migration, troubleshooting, and security documentation;
- package-name and supply-chain checks.

## 0.9.0: release candidate

- frozen 1.0 report schema and compatibility policy;
- clean-environment installation tests;
- performance and failure-mode testing;
- complete rule/check/scenario coverage manifest;
- threat model and MCP safety review;
- public repository quality and release checklist.

## 1.0.0: public release

The release must be installable and useful in an Arc project through the CLI, Python SDK, or MCP. P2Pass may be published later as the first external dogfooding case.

## Quality gates

Before an Arc-specific rule is promoted:

- its protocol premise is versioned and cited;
- ArcReady, Slither, Wake, and Foundry baseline coverage is recorded;
- vulnerable, safe, and edge fixtures pass;
- applicability and unsupported cases are explicit;
- precision is measured on a labeled corpus;
- documentation explains why the result is Arc-specific.

Before each milestone is complete:

- scoped tests, lint, formatting, type checks, and package checks pass;
- public interfaces return the same semantic result;
- unsupported work is reported as `UNKNOWN`, `SKIPPED`, or `NOT_APPLICABLE`;
- changelog and affected profiles/rules are updated.

## Current next milestone

Development starts with 0.1.0. The first implementation step is environment and package scaffolding, followed by the domain model and a thin end-to-end CLI slice. Rule implementation begins only after its evidence fixture and baseline comparison exist.

The first read-only protocol probe will establish the selected Arc profile, capture chain/block evidence, and verify a small set of Arc execution assumptions such as `PREVRANDAO`. It will never send a transaction.

