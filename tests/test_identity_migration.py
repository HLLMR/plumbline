# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Public-interface tests for the controlled identity-migration gate."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "checks" / "check_identity.py"


class IdentityMigrationProcessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "projection").mkdir()
        (self.root / "identity").mkdir()
        ledger_dir = self.root / "examples" / "name-clearance-ledgers"
        ledger_dir.mkdir(parents=True)
        (ledger_dir / "writwall-candidate.json").write_text(
            json.dumps(
                {
                    "candidate": {
                        "display_name": "Writwall",
                        "slug": "writwall",
                    },
                    "disposition": {"decision": "accept"},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (ledger_dir / "plumbline-incident.json").write_text(
            json.dumps(
                {
                    "candidate": {
                        "display_name": "Plumbline",
                        "slug": "plumbline",
                    },
                    "disposition": {"decision": "reject"},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (self.root / "projection" / "public-files.txt").write_text(
            "README.md\nidentity/legacy-references.json\n"
            "projection/public-files.txt\n",
            encoding="utf-8",
        )
        self.manifest = {
            "schema": 1,
            "current": {
                "display_name": "Writwall",
                "slug": "writwall",
                "repository": "https://github.com/HLLMR/writwall",
                "skill": "writwall-adopt",
            },
            "former": {
                "display_name": "Plumbline",
                "slug": "plumbline",
                "retired_on": "2026-08-28",
            },
            "retained": [],
        }

    def run_checker(self) -> subprocess.CompletedProcess[str]:
        (self.root / "identity" / "legacy-references.json").write_text(
            json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8"
        )
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(CHECKER),
                "--root",
                str(self.root),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_unclassified_legacy_match_fails(self) -> None:
        (self.root / "README.md").write_text(
            "# Plumbline\n\nCurrent product copy.\n", encoding="utf-8"
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[legacy] README.md contains an unclassified former-identity match",
            result.stdout,
        )

    def test_stale_current_repository_reference_fails_distinctly(self) -> None:
        (self.root / "README.md").write_text(
            "# Writwall\n\nhttps://github.com/HLLMR/plumbline/actions\n",
            encoding="utf-8",
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[current] README.md contains the former repository coordinate",
            result.stdout,
        )

    def test_missing_current_identity_fails(self) -> None:
        (self.root / "README.md").write_text(
            "# Generic governance toolkit\n", encoding="utf-8"
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[current] public files do not identify Writwall",
            result.stdout,
        )

    def test_unaccounted_legacy_filename_fails(self) -> None:
        legacy = self.root / "docs" / "plumbline-guide.md"
        legacy.parent.mkdir()
        legacy.write_text("# Writwall guide\n", encoding="utf-8")
        allowlist = self.root / "projection" / "public-files.txt"
        allowlist.write_text(
            allowlist.read_text(encoding="utf-8")
            + "docs/plumbline-guide.md\n",
            encoding="utf-8",
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[legacy-path] docs/plumbline-guide.md retains the former slug",
            result.stdout,
        )

    def test_projection_allowlist_mismatch_fails(self) -> None:
        (self.root / "README.md").write_text("# Writwall\n", encoding="utf-8")
        allowlist = self.root / "projection" / "public-files.txt"
        allowlist.write_text(
            allowlist.read_text(encoding="utf-8") + "missing.md\n",
            encoding="utf-8",
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[projection] allowlisted path is missing: missing.md",
            result.stdout,
        )

    def test_retroactive_current_identity_claim_fails(self) -> None:
        (self.root / "README.md").write_text("# Writwall\n", encoding="utf-8")
        about = self.root / "docs" / "about.md"
        about.parent.mkdir()
        about.write_text(
            "Writwall was publicly released on 2026-08-20.\n",
            encoding="utf-8",
        )
        allowlist = self.root / "projection" / "public-files.txt"
        allowlist.write_text(
            allowlist.read_text(encoding="utf-8") + "docs/about.md\n",
            encoding="utf-8",
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[chronology] docs/about.md pairs Writwall with pre-selection date 2026-08-20",
            result.stdout,
        )

    def test_retained_legacy_reference_is_pinned_to_exact_bytes(self) -> None:
        (self.root / "README.md").write_text(
            "# Writwall\n\nFormerly Plumbline.\n", encoding="utf-8"
        )
        self.manifest["retained"] = [
            {
                "path": "README.md",
                "context": "migration_provenance",
                "sha256": "0" * 64,
            }
        ]

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[retained] README.md bytes do not match the manifest digest",
            result.stdout,
        )

    def test_stale_skill_identifier_fails_distinctly(self) -> None:
        (self.root / "README.md").write_text("# Writwall\n", encoding="utf-8")
        start = self.root / "START-HERE.md"
        start.write_text("Install `plumbline-adopt`.\n", encoding="utf-8")
        allowlist = self.root / "projection" / "public-files.txt"
        allowlist.write_text(
            allowlist.read_text(encoding="utf-8") + "START-HERE.md\n",
            encoding="utf-8",
        )

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[current] START-HERE.md contains the former skill identifier",
            result.stdout,
        )

    def test_manifest_identity_must_match_authority_ledgers(self) -> None:
        (self.root / "README.md").write_text("# Writwall\n", encoding="utf-8")
        self.manifest["current"]["display_name"] = "Substitute"
        self.manifest["current"]["slug"] = "substitute"

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[authority] current identity does not match the accepted ledger",
            result.stdout,
        )

    def test_projection_uses_its_pinned_transformed_digest(self) -> None:
        payload = b"# Writwall\n\nFormerly Plumbline.\n"
        (self.root / "README.md").write_bytes(payload)
        (self.root / "PROJECTION-PROVENANCE.md").write_text(
            "# Projection\n", encoding="utf-8"
        )
        self.manifest["retained"] = [
            {
                "path": "README.md",
                "context": "migration_provenance",
                "sha256": "0" * 64,
                "projection_sha256": hashlib.sha256(payload).hexdigest(),
            }
        ]

        result = self.run_checker()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_manifest_schema_fails_closed(self) -> None:
        (self.root / "README.md").write_text("# Writwall\n", encoding="utf-8")
        self.manifest["schema"] = 2

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[manifest] schema must be 1", result.stdout)

    def test_duplicate_retained_path_fails_closed(self) -> None:
        payload = b"# Writwall\n\nFormerly Plumbline.\n"
        (self.root / "README.md").write_bytes(payload)
        entry = {
            "path": "README.md",
            "context": "migration_provenance",
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
        self.manifest["retained"] = [entry, dict(entry)]

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[manifest] duplicate retained path: README.md", result.stdout
        )

    def test_malformed_retained_entry_fails_closed(self) -> None:
        (self.root / "README.md").write_text("# Writwall\n", encoding="utf-8")
        self.manifest["retained"] = [
            {
                "path": "../README.md",
                "context": "",
                "sha256": "not-a-digest",
            }
        ]

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[manifest] retained path must be repository-relative: ../README.md",
            result.stdout,
        )
        self.assertIn(
            "[manifest] retained entry needs non-empty context: ../README.md",
            result.stdout,
        )
        self.assertIn(
            "[manifest] retained entry has invalid sha256: ../README.md",
            result.stdout,
        )

    def test_retained_entry_must_classify_a_former_identity_occurrence(self) -> None:
        payload = b"# Writwall\n\nCurrent-only copy.\n"
        (self.root / "README.md").write_bytes(payload)
        self.manifest["retained"] = [
            {
                "path": "README.md",
                "context": "migration_provenance",
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        ]

        result = self.run_checker()

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[retained] README.md classifies no former-identity occurrence",
            result.stdout,
        )

    def test_projection_accepts_only_the_declared_private_evidence_transform(self) -> None:
        (self.root / "README.md").write_text("# Writwall\n", encoding="utf-8")
        log = self.root / "governance" / "LOG.md"
        log.parent.mkdir()
        log.write_text(
            "[private governed-source identifier omitted]\n", encoding="utf-8"
        )
        allowlist = self.root / "projection" / "public-files.txt"
        allowlist.write_text(
            allowlist.read_text(encoding="utf-8") + "governance/LOG.md\n",
            encoding="utf-8",
        )
        (self.root / "PROJECTION-PROVENANCE.md").write_text(
            "# Projection\n", encoding="utf-8"
        )
        self.manifest["retained"] = [
            {
                "path": "governance/LOG.md",
                "context": "historical_pilot_summary",
                "sha256": "0" * 64,
                "projection_transform": "private_evidence_redaction",
            }
        ]

        result = self.run_checker()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
