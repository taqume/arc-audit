# ArcAudit CLI contract

ArcAudit prints a complete text or JSON report before returning a process status. The process status communicates the highest-priority report condition; it does not replace the report's per-check outcomes or coverage.

## Exit codes

| Code | Meaning | Included outcomes |
| ---: | --- | --- |
| `0` | Analysis completed without a finding or unresolved required work | `PASS`, `NOT_APPLICABLE` |
| `1` | At least one supported Arc-specific finding was produced | `FINDING` |
| `2` | Analysis or input processing failed | `ERROR`, invalid CLI input |
| `3` | Required evidence was incomplete or execution was not permitted | `UNKNOWN`, `SKIPPED` |

Precedence is `ERROR`, then `FINDING`, then incomplete evidence. For example, a report containing both a finding and an unknown result returns `1`; consumers must still inspect the report to see the unknown result.

Running `scan` without `--allow-build` discovers Solidity files but does not execute semantic rules, so it returns `3` when Solidity is present. This prevents an unexecuted scan from appearing successful in shell automation.

Configurable CI policies such as severity thresholds and selectable failure outcomes are intentionally deferred beyond `0.1.0`. Until then, automation should consume the versioned JSON report whenever it needs policy decisions more specific than the codes above.
