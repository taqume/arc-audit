# ARC-SELFDESTRUCT-001: Arc-restricted SELFDESTRUCT beneficiary

## Summary

Arc follows EIP-6780 and applies additional native USDC value rules to `SELFDESTRUCT`. When the contract has a nonzero balance, destruction reverts if the beneficiary is the contract itself, the zero address, a blocklisted address, an already destructed account, or another destination that rejects native value. A successful balance movement emits an EIP-7708 system `Transfer` event.

Arc sources: [`SELFDESTRUCT`](https://docs.arc.io/arc/references/evm-differences#selfdestruct), [value transfer rules](https://docs.arc.io/arc/references/evm-differences#value-transfer-rules), and [restricted-transfer test address](https://docs.arc.io/arc/references/contract-addresses#test-addresses-for-restricted-transfer-behavior).

## Classification

| Field | Value |
| --- | --- |
| Category | Compatibility |
| Default severity | Medium |
| Confidence | High for beneficiary classification; runtime balance remains conditional |
| Engine | Slither IR plus Arc profile addresses |
| Rule version | `1.0.0` |

The finding proves a restricted beneficiary pattern, not that the contract necessarily has a nonzero balance when the path executes. The evidence and summary preserve that runtime condition.

## Detection boundary

The first implementation reports a finding when a `SELFDESTRUCT` beneficiary resolves through a literal or constant-only conversion chain to:

- `address(0)`;
- `address(this)`;
- one of the five Arc custom precompiles in the selected profile; or
- the official seeded blocklisted Arc Testnet address in the selected profile.

An ordinary resolved beneficiary produces `PASS`. An unresolved or dynamic beneficiary produces `UNKNOWN`, never `PASS`. The rule does not yet prove the contract's runtime balance, recognize every blocklisted address, track an account destroyed earlier in the same transaction, or classify arbitrary local-variable aliases.

## Evidence and coverage

Each finding records the beneficiary and its restriction class, the nonzero-balance revert condition, source location, contract and function, selected profile revision, and official sources. Arc Testnet profile revision `2026-09-01.3` adds the seeded blocklisted test address and explicit `SELFDESTRUCT` feature facts.

Fixtures:

- `lab/selfdestruct-beneficiary/`
- `lab/selfdestruct-beneficiary-edge/`
- `lab/selfdestruct-beneficiary-safe/`
- `lab/selfdestruct-beneficiary-unknown/`

## Existing-tool comparison

The Slither baseline reports the fixture's unrestricted functions through its generic `suicidal` detector. Wake has a comparable unprotected-`selfdestruct` detector. Neither baseline classifies Arc's native USDC beneficiary restrictions or the conditional Arc revert. ArcReady's reviewed catalogue did not contain this Solidity `SELFDESTRUCT` semantics rule when `ARC-SELFDESTRUCT-001` was introduced. Foundry compiles the fixtures, but a standard local EVM cannot reproduce Arc's native-value enforcement or EIP-7708 system event.

## Remediation

Use an explicitly permitted beneficiary and make the contract's native USDC balance movement intentional. Avoid zero, self, precompile, and known blocklisted beneficiaries. Handle the EIP-6780 lifecycle separately from Arc's balance-transfer rules, and validate runtime behavior on Arc Testnet when a shutdown flow can hold funds.
