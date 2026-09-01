# ADR 0001: Product direction and delivery strategy

- Status: Accepted
- Date: 2026-09-01

## Decision

ArcAudit will be developed as an independent, local-first Arc security, compatibility, and conformance platform for developers, CI systems, Python applications, and AI agents.

The intended product retains `scan`, `doctor`, `probe`, and Foundry-backed `simulate` capabilities, followed by stable CLI, Python SDK, MCP, SARIF, and CI interfaces. These capabilities will be delivered through versioned milestones that share one core domain and application layer.

ArcReady is a competitive baseline and potential MIT-licensed reference, not the foundation of ArcAudit. Every overlapping capability must either add deeper analysis, stronger evidence, live conformance, broader programmatic access, or be explicitly reused instead of silently duplicated.

Slither is accepted as the main Solidity analysis foundation. ArcAudit will use the `AGPL-3.0-only` public open-source license and preserve all required third-party notices.

P2Pass remains independent. ArcAudit uses its own synthetic and permitted real-world fixture corpus; P2Pass may later demonstrate the released product.

ArcAudit's MCP distribution is local and open source. Operating a paid product or project-hosted MCP service is outside the accepted product plan.

## Consequences

- The final scope remains broad, while public API stability follows evidence and schema stability.
- The core finding/evidence model is implemented before adapter-specific behavior.
- TypeScript is the first offchain language target because EIP-7708 indexing and common wallet integrations require it.
- Arc Testnet is the first live profile; later networks are added only with published, verified profile data.
- Network writes and transaction-producing probes require explicit opt-in.
- A clean result is always qualified by coverage and applicability.
- Users run the MCP server themselves; hosted-service operations and billing are not part of the roadmap.
