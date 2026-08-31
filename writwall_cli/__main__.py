# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Public command-line entry point for Writwall."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="writwall")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "start",
        description="Start with an idea and prepare a governed project handoff.",
        help="Start with an idea",
    )
    privacy = commands.add_parser(
        "privacy",
        description="Manage the local project privacy screen.",
        help="Manage the local privacy screen",
    )
    privacy_commands = privacy.add_subparsers(
        dest="privacy_command", required=True
    )
    for name in ("init", "status"):
        command = privacy_commands.add_parser(name)
        command.add_argument("--project-root", required=True)
    add = privacy_commands.add_parser("add")
    add.add_argument("--project-root", required=True)
    add.add_argument("--identifier-stdin", action="store_true")
    add.add_argument("--confirm-no-secrets", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments or arguments[0] in {"-h", "--help"}:
        build_parser().parse_args(arguments)
        return 0
    if arguments[0] == "privacy":
        from scripts.privacy_screen import main as privacy_main
        return privacy_main(arguments[1:])
    if arguments[0] != "start":
        build_parser().error(f"unknown command: {arguments[0]}")
    from writwall_cli.coordinator import start
    return start(arguments[1:])


if __name__ == "__main__":
    raise SystemExit(main())
