#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Executable contract for pre-adoption expected-denial probes."""

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CANONICAL = REPO_ROOT / "docs" / "bootstrap-charter-addendum.md"
BUNDLED = (REPO_ROOT / "skills" / "writwall-adopt" / "assets" /
           "bootstrap-charter-addendum.md")

REQUIRED = (
    "exact, durably owner-ratified birth-test lifecycle",
    "no active-work-order pointer",
    "confers no mutation authority",
    "denial is the only valid outcome",
    "ordinary no-pointer work remains forbidden",
)

CARRIER_REQUIRED = (
    "bootstrap-charter-addendum.md",
    "ordinary no-pointer",
    "durably owner-ratified",
    "confers no mutation authority",
    "denial is the only valid outcome",
    "any success stops adoption",
)

PERMANENT_TEMPLATE_FORBIDDEN = (
    "bootstrap-charter-addendum",
    "expected-denial",
    "falsification probe",
    "durably owner-ratified birth-test lifecycle",
    "denial is the only valid outcome",
)

CARRIERS = (
    "ADOPTING.md",
    "START-HERE.md",
    "scripts/start_writwall.py",
    "skills/writwall-adopt/SKILL.md",
    "adapters/claude-code/README.md",
    "skills/writwall-adopt/assets/adapters/claude-code/README.md",
)


class BootstrapExpectedDenialContractTests(unittest.TestCase):
    def test_exact_addendum_exists_and_bundle_is_byte_identical(self):
        self.assertTrue(CANONICAL.is_file())
        self.assertTrue(BUNDLED.is_file())
        self.assertEqual(BUNDLED.read_bytes(), CANONICAL.read_bytes())
        text = " ".join(CANONICAL.read_text(encoding="utf-8").lower().split())
        for phrase in REQUIRED:
            self.assertIn(phrase, text)

    def test_every_shipped_carrier_routes_the_exact_addendum_and_contract(self):
        for relative in CARRIERS:
            with self.subTest(relative=relative):
                text = " ".join((REPO_ROOT / relative).read_text(
                    encoding="utf-8").lower().split())
                for phrase in CARRIER_REQUIRED:
                    self.assertIn(phrase, text)

    def test_permanent_charter_template_keeps_ordinary_lockout(self):
        text = (REPO_ROOT / "templates" / "A-charter.md").read_text(
            encoding="utf-8")
        self.assertIn("With no\n      active work order, no mutating action is permitted.", text)
        normalized = " ".join(text.lower().split())
        for phrase in PERMANENT_TEMPLATE_FORBIDDEN:
            self.assertNotIn(phrase, normalized)
        self.assertNotIn(CANONICAL.read_text(encoding="utf-8"), text)

    def test_public_projection_carries_the_addendum(self):
        allowlist = (REPO_ROOT / "projection" / "public-files.txt").read_text(
            encoding="utf-8").splitlines()
        self.assertIn("docs/bootstrap-charter-addendum.md", allowlist)
        self.assertIn(
            "skills/writwall-adopt/assets/bootstrap-charter-addendum.md",
            allowlist,
        )


if __name__ == "__main__":
    unittest.main()
