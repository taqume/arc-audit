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

## External corpus smoke validation

Two first-party Circle repositories were reviewed, pinned to immutable commits, compiled in disposable checkouts, and scanned without a wallet, RPC request, or transaction. Manual labels predicted no finding from the four currently implemented Arc-specific rule families in either production-source set.

| Repository and pin | License boundary | Build stack | Production-source coverage | Observed rule outcomes | Warm scan time |
| --- | --- | --- | ---: | --- | ---: |
| [`circlefin/arc-defi-lend-borrow@d621644`](https://github.com/circlefin/arc-defi-lend-borrow/commit/d621644e29ddac521fefb55dd923adba5c797d0d) | Apache-2.0 repository; MIT Solidity files | Hardhat 2.22, Solidity 0.8.17, Node 24.19.0 | 2 / 2 | 4 `PASS`, 0 `UNKNOWN`, 0 `FINDING` | 9.84 s |
| [`circlefin/refund-protocol@a7ae494`](https://github.com/circlefin/refund-protocol/commit/a7ae494b67ceae4693b416efd52f835d7b53c690) | Apache-2.0 | Foundry 1.7.1, Solidity 0.8.24-compatible | 1 / 1 | 4 `PASS`, 0 `UNKNOWN`, 0 `FINDING` | 0.69 s |

The runs used the `0.1.0` release candidate, Slither `0.11.6`, and `/usr/bin/time -p`. “Warm” means dependencies were already installed and compiler artifacts could be reused; dependency-fetch time is excluded. Upstream source was not copied into ArcAudit.

The first Hardhat run exposed seven dependency-only `UNKNOWN` results from OpenZeppelin. ArcAudit now passes an explicit discovered-source boundary into every Slither rule: dependency contracts remain available to the compiler and semantic graph but cannot independently emit project findings. Foundry `lib`, test, and script trees and Hardhat `node_modules` are excluded from the default production-source boundary. A regression fixture verifies this behavior.

These are negative smoke cases, not a precision percentage or security endorsement. The observed 8 / 8 repository-rule label agreement only shows that the current rules compile and remain quiet on these pinned first-party examples. It does not measure recall, general vulnerability coverage, or whether either upstream project is secure.

### External positive case

The official Apache-2.0 [`circlefin/arc-node@66ad2d5`](https://github.com/circlefin/arc-node/commit/66ad2d5aa6d9b41e8f689812004be4c7233a9e16) corpus supplied a labeled positive case. ArcAudit analyzed all 28 discovered production and mock sources in 7.55 seconds. Source review predicted two supported `ARC-EVM-002` occurrences in `contracts/src/mocks/CallHelper.sol`; ArcAudit reported exactly two findings: `BLOBBASEFEE` at line 143 and `BLOBHASH` at line 165.

The same run returned 17 `UNKNOWN` results for dynamic low-level destinations, native values, and `SELFDESTRUCT` beneficiaries. Those outcomes match the documented constant-resolution boundary and were not counted as findings or false positives. The positive occurrence agreement is 2 / 2; it remains a deliberately small Arc-native case rather than a production-world recall estimate.

## Baseline comparison

- Slither provides compilation and semantic IR. Its generic detectors do not classify the Arc-specific EIP-4788, blob-opcode, native-value destination, or beneficiary predicates implemented here.
- Slither's `suicidal` detector reports unprotected destruction in the `SELFDESTRUCT` fixture, while ArcAudit separately classifies Arc's conditional beneficiary behavior.
- Wake documents comparable generic unchecked-call and unprotected-`selfdestruct` families; the reviewed baseline does not model these Arc profile predicates.
- ArcReady covers selected Arc configuration, `PREVRANDAO`, and offchain blob-transaction patterns. The reviewed catalogue does not cover these four Slither IR rule boundaries.
- Foundry compiles the fixture projects but runs standard EVM semantics and cannot establish Arc's native-value enforcement or EIP-7708 effects.

## Completed quality signals

- vulnerable, safe, edge, and unresolved fixtures for every promoted rule where the distinction applies;
- a malformed Solidity fixture proving compiler failures return bounded `ERROR` evidence without claiming rule execution;
- malformed-layout and unsupported-compiler fixtures proving build failures remain bounded and redact raw compiler output;
- exact Slither-compiled source coverage rather than discovered-file overstatement;
- explicit production-source scoping that prevents dependency, test, and script contracts from emitting project findings;
- explicit partial-coverage reasons when project discovery exceeds the compilation graph;
- `UNKNOWN` instead of `PASS` for supported checks with unresolved critical data flow;
- conservative CLI exit codes that distinguish findings, operational errors, and incomplete evidence;
- pytest, Ruff, strict mypy, Foundry formatting, source distribution, wheel build, and isolated wheel installation;
- read-only Arc Testnet chain, block, and `PREVRANDAO` evidence tied to a versioned profile.

## 0.1.0 milestone disposition

The required foundation evidence is complete: synthetic positive, safe, edge, and unknown labels; external negative Hardhat and Foundry smoke cases; an external Arc-native positive case; bounded failure modes; measured warm scan times; a read-only live Arc probe; and reproducible quality gates.

Optional Arcscan evidence is deferred because it does not add a unique protocol fact to the current static rules or live chain-identity probe. Broader corpus statistics, configurable CI policy, SARIF, suppression behavior, and live transaction scenarios remain later-milestone work.
