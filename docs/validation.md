# ArcAudit 0.1.0 validation status

This document records the current pre-release evidence boundary. The numbers below describe a curated synthetic fixture corpus; they are not estimates of production-world precision or security assurance.

## Automated corpus

| Rule | Expected findings | Expected safe cases | Expected unknown cases | Current agreement |
| --- | ---: | ---: | ---: | ---: |
| `ARC-EVM-001` | 2 | 1 | 1 | 4 / 4 |
| `ARC-EVM-002` | 4 | 1 | 0 | 5 / 5 |
| `ARC-VALUE-001` | 4 | 2 | 1 | 7 / 7 |
| `ARC-SELFDESTRUCT-001` | 6 | 1 | 1 | 8 / 8 |
| **Total** | **16** | **5** | **3** | **24 / 24** |

All expectations are asserted through the public `scan_project` application-service seam with real Foundry compilation and Slither analysis. Internal rule collaborators are not mocked.

The five safe cases produced no rule-family finding, and all 16 supported vulnerable occurrences produced the expected finding in the current fixture corpus. These results only demonstrate agreement on the documented literal, constant-conversion, and direct-opcode boundaries. Dynamic destinations intentionally produce `UNKNOWN` where ArcAudit cannot exclude a restricted runtime value.

## Baseline comparison

- Slither provides compilation and semantic IR. Its generic detectors do not classify the Arc-specific EIP-4788, blob-opcode, native-value destination, or beneficiary predicates implemented here.
- Slither's `suicidal` detector reports unprotected destruction in the `SELFDESTRUCT` fixture, while ArcAudit separately classifies Arc's conditional beneficiary behavior.
- Wake documents comparable generic unchecked-call and unprotected-`selfdestruct` families; the reviewed baseline does not model these Arc profile predicates.
- ArcReady covers selected Arc configuration, `PREVRANDAO`, and offchain blob-transaction patterns. The reviewed catalogue does not cover these four Slither IR rule boundaries.
- Foundry compiles the fixture projects but runs standard EVM semantics and cannot establish Arc's native-value enforcement or EIP-7708 effects.

## Completed quality signals

- vulnerable, safe, edge, and unresolved fixtures for every promoted rule where the distinction applies;
- exact Slither-compiled source coverage rather than discovered-file overstatement;
- explicit partial-coverage reasons when project discovery exceeds the compilation graph;
- `UNKNOWN` instead of `PASS` for supported checks with unresolved critical data flow;
- pytest, Ruff, strict mypy, Foundry formatting, source distribution, wheel build, and isolated wheel installation;
- read-only Arc Testnet chain, block, and `PREVRANDAO` evidence tied to a versioned profile.

## Remaining 0.1.0 review work

- expand beyond synthetic fixtures into a license-reviewed external corpus;
- add explicit compiler-failure and malformed-project regression fixtures;
- measure performance on representative Foundry and Hardhat projects;
- review whether optional read-only Arcscan evidence materially improves the milestone;
- document CLI policy semantics for `UNKNOWN`, `SKIPPED`, and `ERROR` before CI policy exit codes stabilize.
