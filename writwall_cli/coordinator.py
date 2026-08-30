# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Deterministic coordinator for the Writwall command-line interface."""

from __future__ import annotations

from collections.abc import Sequence


def start(argv: Sequence[str] | None = None) -> int:
    """Run the shared coordinator implementation through its supported API."""
    from scripts.start_writwall import main

    return main(list(argv) if argv is not None else None)
