"""Dependency-free report renderers."""

from __future__ import annotations

import json

from arcaudit.domain import Report


def render_json(report: Report) -> str:
    """Render the versioned report contract as deterministic, indented JSON."""

    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def render_text(report: Report) -> str:
    """Render a concise report without hiding unknown or skipped coverage."""

    lines = [
        f"ArcAudit {report.command} report",
        f"Target: {report.target}",
        f"Generated: {report.generated_at}",
    ]
    if report.network:
        lines.append(
            "Network: "
            f"{report.network.profile_id}@{report.network.profile_revision} "
            f"chain={report.network.chain_id} block={report.network.block_number}"
        )
    lines.append("")

    for result in report.results:
        details = [result.outcome.value]
        if result.severity:
            details.append(result.severity.value)
        if result.confidence:
            details.append(f"confidence={result.confidence.value}")
        lines.append(f"[{' | '.join(details)}] {result.check_id}: {result.title}")
        lines.append(f"  {result.summary}")

    counts = report.counts()
    nonzero_counts = [f"{name}={count}" for name, count in counts.items() if count]
    lines.extend(
        [
            "",
            f"Summary: {', '.join(nonzero_counts) if nonzero_counts else 'no checks'}",
            (
                "Coverage: "
                f"considered={report.coverage.files_considered}, "
                f"analyzed={report.coverage.files_analyzed}"
            ),
        ]
    )
    for reason in report.coverage.skipped_reasons:
        lines.append(f"Skipped: {reason}")
    return "\n".join(lines)
