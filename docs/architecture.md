# ArcAudit architecture

## Design objective

ArcAudit exposes one deterministic analysis platform through developer and agent interfaces. Business logic belongs in core application services and analysis engines. CLI, SDK, MCP, CI, and report renderers are adapters.

## Logical structure

```text
ArcAudit Core
├── domain
│   ├── findings
│   ├── evidence
│   ├── coverage
│   ├── policies
│   └── network profiles
├── application services
│   ├── scan
│   ├── doctor
│   ├── probe
│   └── simulate
├── engines
│   ├── Solidity / Slither
│   ├── offchain source and configuration
│   ├── Arc RPC conformance
│   └── Foundry scenarios
└── adapters
    ├── CLI
    ├── Python SDK
    ├── MCP
    ├── JSON / SARIF
    └── GitHub Action
```

Dependencies point inward. Domain models do not import CLI, MCP, Slither, RPC, or Foundry implementations.

## Command responsibilities

### `scan`

Analyzes source and compilation artifacts. It may use Slither, language-specific analyzers, and project metadata. Network access is not required by default.

### `doctor`

Checks project configuration, toolchain availability, recognized network settings, and integration readiness. Offline mode is the default. Online mode performs read-only RPC checks and records the endpoint and network profile used.

### `probe`

Runs narrowly defined protocol conformance checks. Read-only probes are safe by default. Transaction-producing probes require an explicit flag, a Testnet-only policy unless expanded later, and clear cost and secret handling.

### `simulate`

Orchestrates versioned Foundry scenarios. Scenario manifests describe actors, steps, expected findings, and supported backends. Foundry performs EVM execution; ArcAudit interprets evidence and states which Arc behavior was or was not reproduced.

## Finding contract

Every check returns an explicit outcome:

```text
PASS | FINDING | UNKNOWN | NOT_APPLICABLE | ERROR | SKIPPED
```

`severity` applies to findings. `confidence`, `applicability`, `evidence`, and `coverage` remain independent fields.

Minimum report metadata:

- rule and rule version;
- network profile and activation boundary, when applicable;
- outcome, severity, and confidence;
- observed and expected behavior;
- source locations or RPC/transaction evidence;
- analyzed languages, files, and artifacts;
- unresolved inputs and skipped coverage;
- supporting source URLs and verification timestamp.

## Network profiles

A profile is data, not scattered constants. It records at least:

```text
profile_id
network_name
chain_id
deployment_phase
effective_from
evm_baseline
protocol_features
system_contracts
event_emitters
rpc_expectations
source_urls
verified_at
```

If a required profile or activation boundary cannot be resolved, the affected check cannot return `PASS`.

## Safety boundaries

- Repository contents are untrusted input.
- Commands discovered in a target project are not executed implicitly.
- Secrets are never included in findings, logs, snapshots, or MCP responses.
- RPC timeouts, malformed responses, and rate limits produce `UNKNOWN` or `ERROR`, not protocol findings.
- MCP tools are read-only by default and use structured, bounded output.
- A clean report communicates observed coverage, not an assurance claim.

## Implementation documentation

Public APIs and non-obvious security-sensitive functions receive concise English docstrings. Inline comments explain protocol constraints, evidence decisions, or unusual control flow. Obvious operations do not need narration.

