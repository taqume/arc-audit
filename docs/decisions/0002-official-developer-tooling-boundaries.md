# ADR 0002: Official developer-tooling boundaries

- Status: Accepted
- Date: 2026-09-01

## Context

Arc documents standard EVM tools, Circle SDKs, public RPC and explorer services, transaction extensions, an official node stack, and third-party infrastructure providers. These surfaces have different owners, authentication requirements, release cycles, and network identifiers.

The same Arc Testnet is represented as chain ID `5042002`, App Kit identifier `Arc_Testnet`, Circle Wallet API identifier `ARC-TESTNET`, Gateway identifier `arcTestnet`, and CCTP/Gateway domain `26`. Treating these namespaces as interchangeable would create incorrect doctor findings.

## Decision

- No Arc or Circle SDK is a core ArcAudit dependency.
- Foundry is the primary Solidity fixture and scenario backend, but `scan` and offline `doctor` remain usable without it.
- Hardhat is supported through a separate project adapter and secondary fixtures.
- Arc Testnet RPC and Arcscan/Blockscout are opt-in, read-only evidence adapters.
- Circle Faucet remains a manual Testnet prerequisite and documentation link; ArcAudit will not automate faucet interaction.
- App Kit, Circle Wallets, Circle Contracts, CCTP, Gateway, and Circle CLI are optional integration packs activated only by clear project signals.
- Memo, CallFrom, Multicall3From, EIP-7708, protocol activations, and address provenance are versioned profile/rule data.
- `arcup` and Docker Compose operate the resource-intensive Arc node stack; they are not a lightweight local Arc devnet. Self-hosted node support is an advanced conformance and node-doctor target.
- Official Arc sample repositories may become pinned, license-reviewed regression fixtures. Their official status is not treated as an audit assurance.
- Third-party providers listed by Arc remain third-party and are labeled as such in evidence.

## Consequences

- ArcAudit's default installation stays Python-centered and local-first.
- Remote adapters record endpoint class, chain ID, block, profile revision, timeout, and provenance.
- Product-specific identifiers are validated against the detected SDK or configuration namespace.
- Authenticated SDK/API tests stay out of the default test suite and require explicit credentials and opt-in.
- Full-node tests run only in a dedicated advanced or scheduled environment.

## Evidence

The versioned Arc Testnet profile records the selected endpoints, addresses, identifiers, activation boundaries, and direct public sources. The primary official references are Arc's [deployment model](https://docs.arc.io/arc/concepts/deployment-model), [developer tools](https://docs.arc.io/arc/tools), [RPC endpoints](https://docs.arc.io/arc/references/rpc-endpoints), and [contract addresses](https://docs.arc.io/arc/references/contract-addresses).
