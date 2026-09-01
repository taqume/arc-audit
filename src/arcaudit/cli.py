"""Thin command-line adapter over ArcAudit application services."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from arcaudit.domain import Outcome, Report
from arcaudit.profiles import ProfileNotFoundError, load_profile
from arcaudit.reporting import render_json, render_text
from arcaudit.services.doctor import doctor_project
from arcaudit.services.probe import probe_network
from arcaudit.services.scan import scan_project
from arcaudit.version import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI grammar without executing application logic."""

    parser = argparse.ArgumentParser(
        prog="arcaudit",
        description="Arc security, compatibility, and conformance tooling",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="analyze project source")
    scan_parser.add_argument("target", nargs="?", default=".")
    scan_parser.add_argument(
        "--allow-build",
        action="store_true",
        help="allow Slither to invoke the detected compiler framework",
    )
    _add_common_report_arguments(scan_parser)

    doctor_parser = subparsers.add_parser("doctor", help="inspect project configuration")
    doctor_parser.add_argument("target", nargs="?", default=".")
    _add_common_report_arguments(doctor_parser)

    probe_parser = subparsers.add_parser("probe", help="run read-only Arc RPC checks")
    probe_parser.add_argument("--rpc-url", help="override the profile's public HTTP endpoint")
    _add_common_report_arguments(probe_parser)

    profile_parser = subparsers.add_parser("profile", help="inspect bundled network profiles")
    profile_subparsers = profile_parser.add_subparsers(dest="profile_command", required=True)
    profile_show_parser = profile_subparsers.add_parser("show", help="show one profile")
    profile_show_parser.add_argument("profile_id", nargs="?", default="arc-testnet")
    profile_show_parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Execute the selected command and return a process-friendly status code."""

    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "profile":
            profile = load_profile(arguments.profile_id)
            if arguments.format == "json":
                print(json.dumps(profile.to_dict(), indent=2, sort_keys=True))
            else:
                print(
                    f"{profile.profile_id}@{profile.revision} "
                    f"chain={profile.chain_id} verified={profile.verified_at}"
                )
            return 0

        profile = load_profile(arguments.profile)
        if arguments.command == "scan":
            report = scan_project(arguments.target, profile, allow_build=arguments.allow_build)
        elif arguments.command == "doctor":
            report = doctor_project(arguments.target, profile)
        elif arguments.command == "probe":
            report = probe_network(profile, rpc_url=arguments.rpc_url)
        else:  # pragma: no cover - argparse constrains this branch
            parser.error(f"unsupported command: {arguments.command}")
            return 2
    except (ProfileNotFoundError, ValueError) as error:
        parser.error(str(error))
        return 2

    _print_report(report, arguments.format)
    return _report_exit_code(report)


def entrypoint() -> None:
    """Console-script entry point."""

    raise SystemExit(main())


def _add_common_report_arguments(parser: argparse.ArgumentParser) -> None:
    """Add consistent profile and output arguments to report commands."""

    parser.add_argument("--profile", default="arc-testnet")
    parser.add_argument("--format", choices=("text", "json"), default="text")


def _print_report(report: Report, output_format: str) -> None:
    """Render one report through the requested adapter."""

    print(render_json(report) if output_format == "json" else render_text(report))


def _report_exit_code(report: Report) -> int:
    """Map report outcomes to the conservative 0.1 process-status contract."""

    outcomes = {result.outcome for result in report.results}
    if Outcome.ERROR in outcomes:
        return 2
    if Outcome.FINDING in outcomes:
        return 1
    if outcomes & {Outcome.UNKNOWN, Outcome.SKIPPED}:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
