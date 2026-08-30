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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments or arguments[0] in {"-h", "--help"}:
        build_parser().parse_args(arguments)
        return 0
    if arguments[0] != "start":
        build_parser().error(f"unknown command: {arguments[0]}")
    from writwall_cli.coordinator import start
    return start(arguments[1:])


if __name__ == "__main__":
    raise SystemExit(main())
