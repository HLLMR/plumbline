# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Public-process tests for the clean-history projection commands."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import hashlib
import importlib.util
import os
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILDER = REPO_ROOT / "scripts" / "build_public_projection.py"
CHECKER = REPO_ROOT / "checks" / "check_public_projection.py"


def load_projection_checker():
    spec = importlib.util.spec_from_file_location(
        "wo_pl_031_check_public_projection", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicProjectionProcessTests(unittest.TestCase):
    def test_complete_ledger_matches_independent_full_line_vector(self):
        from scripts.build_public_projection import complete_tree_ledger
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a").write_bytes(b"z")
            (root / "b").write_bytes(b"a")
            (root / "PROJECTION-MANIFEST.sha256").write_bytes(b"manifest\n")
            lines = [
                hashlib.sha256(b"z").hexdigest() + "  a",
                hashlib.sha256(b"a").hexdigest() + "  b",
                hashlib.sha256(b"manifest\n").hexdigest() + "  PROJECTION-MANIFEST.sha256",
            ]
            expected = hashlib.sha256(("\n".join(sorted(lines)) + "\n").encode("utf-8")).hexdigest()
            self.assertEqual(complete_tree_ledger(root), expected)
            command = subprocess.run(
                [sys.executable, "-B", str(BUILDER), "--complete-tree-ledger", str(root)],
                cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(command.returncode, 0, command.stdout + command.stderr)
            self.assertEqual(command.stdout.strip(), expected)
            (root / "b").rename(root / "renamed")
            self.assertNotEqual(complete_tree_ledger(root), expected)
            renamed = complete_tree_ledger(root)
            (root / "PROJECTION-MANIFEST.sha256").write_bytes(b"changed\n")
            self.assertNotEqual(complete_tree_ledger(root), renamed)

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(__import__("shutil").rmtree, self.tmp, True)
        self.source = self.tmp / "source"
        self.output = self.tmp / "candidate"
        self.patterns = self.tmp / "private-patterns.txt"
        self.state = self.tmp / "state"
        (self.source / "projection").mkdir(parents=True)
        (self.source / "README.md").write_text("# Public fixture\n", encoding="utf-8")
        (self.source / "projection" / "public-files.txt").write_text(
            "README.md\nprojection/public-files.txt\n", encoding="utf-8")
        self.patterns.write_text("PRIVATE_" + "NEEDLE\n", encoding="utf-8")

    def run_builder(self, *, source: Path | None = None,
                    output: Path | None = None,
                    patterns: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(BUILDER),
             "--source-root", str(source or self.source),
             "--output", str(output or self.output),
             "--private-pattern-file", str(patterns or self.patterns)],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)

    def run_checker(self, *, output: Path | None = None,
                    source: Path | None = None,
                    patterns: Path | None = None) -> subprocess.CompletedProcess[str]:
        source_root = (source or self.source).resolve()
        if source_root == REPO_ROOT:
            checker = CHECKER
        else:
            checker = source_root / "checks" / "check_public_projection.py"
            checker.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(CHECKER, checker)
            privacy_module = source_root / "scripts" / "privacy_screen.py"
            privacy_module.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO_ROOT / "scripts" / "privacy_screen.py", privacy_module)
        return subprocess.run(
            [sys.executable, "-B", str(checker), str(output or self.output),
             "--private-pattern-file", str(patterns or self.patterns)],
            cwd=source_root, capture_output=True, text=True, timeout=60)

    def managed_environment(self) -> dict[str, str]:
        environment = os.environ.copy()
        environment["WRITWALL_STATE_HOME"] = str(self.state)
        return environment

    def test_builder_and_checker_use_the_managed_project_profile_by_default(self) -> None:
        initialized = subprocess.run(
            [sys.executable, "-B", "-m", "writwall_cli", "privacy", "init",
             "--project-root", str(self.source)],
            cwd=REPO_ROOT, env=self.managed_environment(), capture_output=True,
            text=True, timeout=30,
        )
        self.assertEqual(initialized.returncode, 0, initialized.stderr)

        built = subprocess.run(
            [sys.executable, "-B", str(BUILDER), "--source-root", str(self.source),
             "--output", str(self.output)],
            cwd=REPO_ROOT, env=self.managed_environment(), capture_output=True,
            text=True, timeout=60,
        )
        checker = self.source / "checks" / "check_public_projection.py"
        checker.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(CHECKER, checker)
        privacy_module = self.source / "scripts" / "privacy_screen.py"
        privacy_module.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / "scripts" / "privacy_screen.py", privacy_module)
        checked = subprocess.run(
            [sys.executable, "-B", str(checker), str(self.output)],
            cwd=self.source, env=self.managed_environment(), capture_output=True,
            text=True, timeout=60,
        )

        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        combined = built.stdout + built.stderr + checked.stdout + checked.stderr
        self.assertNotIn(str(self.state), combined)

    def test_missing_managed_profile_fails_closed_without_disclosing_location(self) -> None:
        built = subprocess.run(
            [sys.executable, "-B", str(BUILDER), "--source-root", str(self.source),
             "--output", str(self.output)],
            cwd=REPO_ROOT, env=self.managed_environment(), capture_output=True,
            text=True, timeout=60,
        )

        self.assertNotEqual(built.returncode, 0)
        self.assertIn("writwall privacy init", built.stdout + built.stderr)
        self.assertNotIn(str(self.state), built.stdout + built.stderr)
        self.assertNotIn("Traceback", built.stdout + built.stderr)

    def test_candidate_cleanup_does_not_delete_the_managed_profile(self) -> None:
        initialized = subprocess.run(
            [sys.executable, "-B", "-m", "writwall_cli", "privacy", "init",
             "--project-root", str(self.source)],
            cwd=REPO_ROOT, env=self.managed_environment(), capture_output=True,
            text=True, timeout=30,
        )
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        built = subprocess.run(
            [sys.executable, "-B", str(BUILDER), "--source-root", str(self.source),
             "--output", str(self.output)],
            cwd=REPO_ROOT, env=self.managed_environment(), capture_output=True,
            text=True, timeout=60,
        )
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)

        shutil.rmtree(self.output)

        profiles = list(self.state.rglob("private-patterns.txt"))
        self.assertEqual(len(profiles), 1)
        status = subprocess.run(
            [sys.executable, "-B", "-m", "writwall_cli", "privacy", "status",
             "--project-root", str(self.source)],
            cwd=REPO_ROOT, env=self.managed_environment(), capture_output=True,
            text=True, timeout=30,
        )
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)

    def allow(self, relative: str, content: str) -> None:
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.allow_path(relative)

    def allow_bytes(self, relative: str, content: bytes) -> None:
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        self.allow_path(relative)

    def allow_path(self, relative: str) -> None:
        allowlist = self.source / "projection" / "public-files.txt"
        entries = [line for line in allowlist.read_text(encoding="utf-8").splitlines()
                   if line]
        entries.append(relative)
        allowlist.write_text("\n".join(sorted(entries)) + "\n", encoding="utf-8")

    def refresh_manifest_digest(self, relative: str) -> None:
        manifest = self.output / "PROJECTION-MANIFEST.sha256"
        digest = hashlib.sha256((self.output / relative).read_bytes()).hexdigest()
        lines = manifest.read_text(encoding="utf-8").splitlines()
        lines = [f"{digest}  {relative}" if line.endswith(f"  {relative}") else line
                 for line in lines]
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def remove_manifest_entry(self, relative: str) -> None:
        manifest = self.output / "PROJECTION-MANIFEST.sha256"
        lines = [line for line in manifest.read_text(encoding="utf-8").splitlines()
                 if not line.endswith(f"  {relative}")]
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_clean_build_copies_only_the_allowlist_and_generates_records(self) -> None:
        result = self.run_builder()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        files = sorted(
            path.relative_to(self.output).as_posix()
            for path in self.output.rglob("*") if path.is_file())
        self.assertEqual(files, [
            "PROJECTION-MANIFEST.sha256",
            "PROJECTION-PROVENANCE.md",
            "README.md",
            "projection/public-files.txt",
        ])

    def test_binary_readme_asset_is_projected_byte_identically(self) -> None:
        relative = "docs/assets/writwall-og.png"
        payload = b"\x89PNG\r\n\x1a\nwritwall"
        self.allow_bytes(relative, payload)

        result = self.run_builder()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.output / relative).read_bytes(), payload)
        manifest = (self.output / "PROJECTION-MANIFEST.sha256").read_text(
            encoding="utf-8")
        self.assertIn(f"{hashlib.sha256(payload).hexdigest()}  {relative}", manifest)

    def test_projected_decision_references_state_the_private_boundary(self) -> None:
        """Public records must not imply that omitted project decisions ship."""
        decisions = (REPO_ROOT / "decisions" / "README.md").read_text(
            encoding="utf-8")
        state = (REPO_ROOT / "governance" / "STATE.md").read_text(
            encoding="utf-8")

        self.assertIn(
            "DR-002 is intentionally unused in the methodology series",
            decisions,
        )
        references = [
            line for line in state.splitlines()
            if "`governance/decisions/DR-003.md`" in line
        ]
        self.assertGreaterEqual(len(references), 2)
        for line in references:
            self.assertIn("private governed-source record", line)
            self.assertIn("not carried by public candidates", line)

    def test_projection_host_path_match_is_boundary_aware(self) -> None:
        checker = load_projection_checker()
        shallow_home = "/" + "root"
        self.assertFalse(checker.machine_path_occurs(
            "nested/root-relative Markdown targets", shallow_home))
        self.assertTrue(checker.machine_path_occurs(
            "repository: " + shallow_home + "/Projects/example", shallow_home))
        self.assertTrue(checker.machine_path_occurs(
            "Home is " + shallow_home + ".", shallow_home))

    def test_contributing_command_is_transformed_only_in_projection(self) -> None:
        source_command = "python -B checks/check_distribution.py"
        projection_command = source_command + " --projection"
        source_text = (
            "# Contributing\n\n"
            "Governed source uses:\n\n"
            f"```text\n{source_command}\n```\n"
        )
        self.allow("CONTRIBUTING.md", source_text)
        built = self.run_builder()
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        self.assertEqual(
            (self.source / "CONTRIBUTING.md").read_text(encoding="utf-8"),
            source_text,
        )
        projected = (self.output / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn(projection_command, projected)
        self.assertNotIn(source_command + "\n", projected)

        second = self.tmp / "candidate-two"
        rebuilt = self.run_builder(source=self.output, output=second)
        self.assertEqual(rebuilt.returncode, 0, rebuilt.stdout + rebuilt.stderr)
        self.assertEqual(
            (second / "CONTRIBUTING.md").read_text(encoding="utf-8"),
            projected,
        )

    def test_real_public_contributing_command_matches_projection_mode(self) -> None:
        built = self.run_builder(source=REPO_ROOT)
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        contributing = (self.output / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("python -B checks/check_distribution.py --projection", contributing)

    def test_duplicate_allowlist_entry_fails(self) -> None:
        (self.source / "projection" / "public-files.txt").write_text(
            "README.md\nREADME.md\nprojection/public-files.txt\n", encoding="utf-8")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate", result.stdout + result.stderr)

    def test_unsorted_allowlist_fails(self) -> None:
        (self.source / "projection" / "public-files.txt").write_text(
            "projection/public-files.txt\nREADME.md\n", encoding="utf-8")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sorted", result.stdout + result.stderr)

    def test_allowlist_path_escape_fails_before_copy(self) -> None:
        (self.tmp / "secret.txt").write_text("outside\n", encoding="utf-8")
        (self.source / "projection" / "public-files.txt").write_text(
            "../secret.txt\nprojection/public-files.txt\n", encoding="utf-8")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unsafe", result.stdout + result.stderr)

    def test_allowlisted_symlink_fails(self) -> None:
        target = self.tmp / "outside.txt"
        target.write_text("outside\n", encoding="utf-8")
        link = self.source / "linked.txt"
        try:
            link.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"symlink unavailable: {exc}")
        (self.source / "projection" / "public-files.txt").write_text(
            "linked.txt\nprojection/public-files.txt\n", encoding="utf-8")
        result = self.run_builder()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stdout + result.stderr)

    def test_clean_candidate_passes_independent_checker(self) -> None:
        built = self.run_builder()
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_active_governance_record_fails_projection_check(self) -> None:
        self.allow("governance/STATE.md", "---\nstatus: ACTIVE\n---\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("active governance", (checked.stdout + checked.stderr).lower())

    def test_unqualified_public_history_recoverability_claim_fails(self) -> None:
        self.allow("decisions/DR-001.md", "The object is recoverable from Git history.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        projected = self.output / "decisions" / "DR-001.md"
        projected.write_text("The object is recoverable from Git history.\n",
                             encoding="utf-8")
        self.refresh_manifest_digest("decisions/DR-001.md")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("recoverability", (checked.stdout + checked.stderr).lower())

    def test_builder_qualifies_private_source_recoverability_claim(self) -> None:
        self.allow("decisions/DR-001.md", "The object is recoverable from Git history.\n")
        built = self.run_builder()
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        projected = (self.output / "decisions" / "DR-001.md").read_text(encoding="utf-8")
        self.assertIn("private governed source", projected)

    def test_retained_archive_reference_without_note_fails(self) -> None:
        """WO-PL-023 B.3.5 retained-reference integrity, RED case.

        A projected document that names a specific path under an omitted
        private directory (archive/, governance/history/, dist/) without the
        exact retained-reference note is stale relative to the candidate: a
        reader cannot resolve it, and nothing marks that fact truthfully.
        """
        self.allow("NOTES.md",
                   "See `archive/pre-adoption-bootstrap/README.md` for detail.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("retains an unresolved reference",
                      checked.stdout + checked.stderr)

    def test_retained_archive_reference_with_note_passes(self) -> None:
        """WO-PL-023 B.3.5 retained-reference integrity, GREEN case."""
        self.allow("NOTES.md",
                   "See `archive/pre-adoption-bootstrap/README.md` "
                   "(private governed-source reference, not present in this candidate) "
                   "for detail.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_plain_omitted_archive_history_and_dist_references_fail(self) -> None:
        """Concrete omitted paths are references even without backticks."""
        self.allow(
            "NOTES.md",
            "See archive/private/README.md, governance/history/WO-OLD.md, "
            "and dist/writwall.zip for detail.\n",
        )
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("retains an unresolved reference",
                      checked.stdout + checked.stderr)

    def test_markdown_omitted_archive_history_and_dist_links_fail(self) -> None:
        """Concrete omitted paths used as Markdown link targets also fail."""
        self.allow(
            "NOTES.md",
            "See [archive](archive/private/README.md), "
            "[history](governance/history/WO-OLD.md), and "
            "[bundle](dist/writwall.zip).\n",
        )
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("retains an unresolved reference",
                      checked.stdout + checked.stderr)

    def test_nested_markdown_omitted_links_fail(self) -> None:
        self.allow(
            "nested/NOTES.md",
            "See [archive](../archive/private/README.md), "
            "[history](../../governance/history/WO-OLD.md), "
            "[bundle](./dist/writwall.zip), and "
            "[root](/archive/old.md).\n",
        )
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("retains an unresolved reference",
                      checked.stdout + checked.stderr)

    def test_plain_omitted_reference_with_note_passes(self) -> None:
        self.allow(
            "NOTES.md",
            "See archive/private/README.md "
            "(private governed-source reference, not present in this candidate).\n",
        )
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_sentence_final_plain_omitted_reference_fails(self) -> None:
        self.allow("NOTES.md", "See governance/history/WO-OLD.md.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("retains an unresolved reference",
                      checked.stdout + checked.stderr)

    def test_query_bearing_markdown_omitted_link_fails(self) -> None:
        self.allow(
            "NOTES.md",
            'See [history](<../governance/history/WO-OLD.md?view=1> "old").\n',
        )
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("retains an unresolved reference",
                      checked.stdout + checked.stderr)

    def test_builder_annotates_known_governed_source_reference_in_candidate_only(self) -> None:
        source_text = ("A.4.9 `archive/**` -> `archive/README.md`; archived "
                       "material is evidence only.\n")
        relative = "decisions/DR-001.md"
        self.allow(relative, source_text)
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertEqual((self.source / relative).read_text(encoding="utf-8"),
                         source_text)
        projected = (self.output / relative).read_text(encoding="utf-8")
        self.assertIn("private governed-source reference", projected)

    def test_builder_marks_migration_guide_path_as_target_project_reference(self) -> None:
        source_text = ("| draft | Move to `archive/DR-001_draft_unratified.md`. "
                       "| DC.3.4 |\n")
        relative = "migration-guides/0.1-to-0.6.md"
        self.allow(relative, source_text)
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        projected = (self.output / relative).read_text(encoding="utf-8")
        self.assertIn("target-project path, not a candidate member", projected)

    def test_builder_qualifies_dr005_report_reference_in_candidate_only(self) -> None:
        source_text = ("See `governance/reports/WO-PL-021-report.md` for the "
                       "underlying evidence.\n")
        self.allow("decisions/DR-005.md", source_text)
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertEqual((self.source / "decisions" / "DR-005.md").read_text(
            encoding="utf-8"), source_text)
        projected = (self.output / "decisions" / "DR-005.md").read_text(
            encoding="utf-8")
        self.assertIn("private governed-source reference", projected)

    def test_retained_archive_reference_with_target_project_note_passes(self) -> None:
        self.allow("NOTES.md",
                   "Create `archive/project-history.md` "
                   "(target-project path, not a candidate member).\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_bare_omitted_directory_mention_does_not_false_positive(self) -> None:
        """A trailing-slash directory mention names no specific unresolved
        file and must not be flagged; only a concrete sub-path reference is."""
        self.allow("NOTES.md",
                   "Closed history lives under `governance/history/` generally.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_stale_repository_inventory_heading_without_candidate_distinction_fails(self) -> None:
        """WO-PL-022 B.3 item 3 / item 6, stale-candidate-inventory case.

        A projected document that carries the bare "What is in this
        repository" inventory heading, without also distinguishing the
        private governed source, the source distribution, and the
        positive-allowlist candidate the reader is actually looking at, is
        stale relative to the candidate it ships inside. This is isolated
        from every other gate: the minimal synthetic fixture here carries no
        license or distribution checker entries, so only the new inventory
        reason can fail this run, independent of the real source's missing
        pilot example or any other integrated gate.
        """
        self.allow("INVENTORY.md",
                   "## What is in this repository\n\n"
                   "A tree of the private governed source.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        combined = (checked.stdout + checked.stderr).lower()
        self.assertIn("inventory", combined)
        self.assertNotIn("license", combined)
        self.assertNotIn("distribution", combined)

    def test_unclassified_commit_identifier_fails(self) -> None:
        identifier = "1" * 40
        (self.source / "README.md").write_text(
            f"Private source commit `{identifier}`.\n", encoding="utf-8")
        self.assertEqual(self.run_builder().returncode, 0)
        provenance = self.output / "PROJECTION-PROVENANCE.md"
        lines = [line for line in provenance.read_text(encoding="utf-8").splitlines()
                 if identifier not in line]
        provenance.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.refresh_manifest_digest("PROJECTION-PROVENANCE.md")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("unclassified", (checked.stdout + checked.stderr).lower())

    def test_uppercase_full_identifier_is_inventoried(self) -> None:
        identifier = "ABCDEF" * 6 + "ABCD"
        (self.source / "README.md").write_text(
            f"Private source commit `{identifier}`.\n", encoding="utf-8")
        built = self.run_builder()
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        provenance = (self.output / "PROJECTION-PROVENANCE.md").read_text(
            encoding="utf-8")
        self.assertIn(identifier, provenance)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_actual_host_path_fails_without_echoing_it(self) -> None:
        needle = self.source.as_posix()
        (self.source / "README.md").write_text(
            f"Accidental machine path: {needle}\n", encoding="utf-8")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        combined = checked.stdout + checked.stderr
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("host-specific", combined.lower())
        self.assertNotIn(needle, combined)

    def test_concrete_foreign_windows_path_in_current_plan_fails_without_echoing_it(self) -> None:
        needle = r"Z:\client\media"
        self.allow("governance/PLAN.md", f"Current corpus: `{needle}`.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        combined = checked.stdout + checked.stderr
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("host-specific", combined.lower())
        self.assertNotIn(needle, combined)

    def test_concrete_foreign_posix_home_path_in_current_state_fails_without_echoing_it(self) -> None:
        needle = "/home/alice/client-media"
        self.allow("governance/STATE.md", f"Current corpus: `{needle}`.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        combined = checked.stdout + checked.stderr
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("host-specific", combined.lower())
        self.assertNotIn(needle, combined)

    def test_concrete_foreign_macos_path_in_current_plan_fails_without_echoing_it(self) -> None:
        needle = "/Users/alice/client-media"
        self.allow("governance/PLAN.md", f"Current corpus: `{needle}`.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        combined = checked.stdout + checked.stderr
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("host-specific", combined.lower())
        self.assertNotIn(needle, combined)

    def test_concrete_foreign_mounted_drive_path_in_current_plan_fails_without_echoing_it(self) -> None:
        needle = "/mnt/z/client-media"
        self.allow("governance/PLAN.md", f"Current corpus: `{needle}`.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        combined = checked.stdout + checked.stderr
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("host-specific", combined.lower())
        self.assertNotIn(needle, combined)

    def test_canonical_windows_and_posix_placeholders_remain_allowed(self) -> None:
        (self.source / "README.md").write_text(
            "Windows: `C:\\path\\to\\your-project`\n"
            "POSIX: `/path/to/your-project`\n",
            encoding="utf-8",
        )
        built = self.run_builder()
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_empty_inherited_git_directory_fails(self) -> None:
        self.assertEqual(self.run_builder().returncode, 0)
        (self.output / ".git").mkdir()
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("git metadata", (checked.stdout + checked.stderr).lower())

    def test_empty_private_archive_directory_fails(self) -> None:
        self.assertEqual(self.run_builder().returncode, 0)
        (self.output / "archive").mkdir()
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("denied directory", (checked.stdout + checked.stderr).lower())

    def test_stale_zip_fails_with_specific_category(self) -> None:
        self.assertEqual(self.run_builder().returncode, 0)
        (self.output / "stale.zip").write_bytes(b"not a release candidate")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("stale archive", (checked.stdout + checked.stderr).lower())

    def test_projection_checker_runs_candidate_license_gate(self) -> None:
        built = self.run_builder(source=REPO_ROOT)
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        (self.output / "LICENSE").write_text("drifted license\n", encoding="utf-8")
        self.refresh_manifest_digest("LICENSE")
        checked = self.run_checker(source=REPO_ROOT)
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("license", (checked.stdout + checked.stderr).lower())

    def test_projection_checker_runs_candidate_distribution_gate(self) -> None:
        built = self.run_builder(source=REPO_ROOT)
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        readme = self.output / "README.md"
        readme.write_bytes(readme.read_bytes().replace(
            b"document-controlled governance methodology",
            b"loosely controlled governance methodology", 1))
        self.refresh_manifest_digest("README.md")
        checked = self.run_checker(source=REPO_ROOT)
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("distribution", (checked.stdout + checked.stderr).lower())

    def test_real_public_surface_builds_and_passes_integrated_checks(self) -> None:
        built = self.run_builder(source=REPO_ROOT)
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        checked = self.run_checker(source=REPO_ROOT)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_candidate_archives_are_rebuilt_and_byte_identical(self) -> None:
        built = self.run_builder(source=REPO_ROOT)
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        outputs = [self.tmp / "archive-one", self.tmp / "archive-two"]
        archives = []
        for output in outputs:
            result = subprocess.run(
                [sys.executable, "-B", str(self.output / "scripts" /
                                             "build_distribution.py"),
                 "--output", str(output)],
                cwd=self.output, capture_output=True, text=True, timeout=300)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            archives.append(next(output.glob("*.zip")))
        self.assertEqual(archives[0].read_bytes(), archives[1].read_bytes())
        checked = subprocess.run(
            [sys.executable, "-B", str(self.output / "checks" /
                                         "check_distribution.py"),
             "--projection", "--archive", str(archives[0])],
            cwd=self.output, capture_output=True, text=True, timeout=300)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_nonempty_output_fails_without_overwriting(self) -> None:
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_text("keep\n", encoding="utf-8")
        built = self.run_builder()
        self.assertNotEqual(built.returncode, 0)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")

    def test_private_pattern_match_fails_without_echoing_value(self) -> None:
        self.assertEqual(self.run_builder().returncode, 0)
        private_value = self.patterns.read_text(encoding="utf-8").strip()
        readme = self.output / "README.md"
        readme.write_text(private_value + "\n", encoding="utf-8")
        self.refresh_manifest_digest("README.md")
        checked = self.run_checker()
        combined = checked.stdout + checked.stderr
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("private disclosure", combined.lower())
        self.assertNotIn(private_value, combined)

    def test_private_pattern_is_redacted_only_from_retained_public_evidence(self) -> None:
        private_value = self.patterns.read_text(encoding="utf-8").strip()
        self.allow(
            "governance/LOG.md",
            f"Historical private source reference: {private_value}.\n",
        )

        built = self.run_builder()

        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        projected = (self.output / "governance" / "LOG.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn(private_value, projected)
        self.assertIn("[private governed-source identifier omitted]", projected)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_projection_only_truth_transforms_are_idempotent(self) -> None:
        self.allow(
            "decisions/DR-001.md",
            "The original remains recoverable from Git history.\n",
        )
        self.allow("governance/STATE.md", "# Writwall state\n")
        first = self.run_builder()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        second_output = self.tmp / "candidate-two"

        second = self.run_builder(source=self.output, output=second_output)

        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        for relative in ("decisions/DR-001.md", "governance/STATE.md"):
            self.assertEqual(
                (self.output / relative).read_bytes(),
                (second_output / relative).read_bytes(),
                relative,
            )

    def test_manifest_tamper_fails(self) -> None:
        self.assertEqual(self.run_builder().returncode, 0)
        (self.output / "README.md").write_text("tampered\n", encoding="utf-8")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("digest mismatch", (checked.stdout + checked.stderr).lower())

    def test_self_consistent_truncated_allowlist_fails_source_binding(self) -> None:
        self.assertEqual(self.run_builder().returncode, 0)
        allowlist = self.output / "projection" / "public-files.txt"
        old_digest = hashlib.sha256(allowlist.read_bytes()).hexdigest()
        allowlist.write_text("projection/public-files.txt\n", encoding="utf-8")
        new_digest = hashlib.sha256(allowlist.read_bytes()).hexdigest()
        (self.output / "README.md").unlink()
        provenance = self.output / "PROJECTION-PROVENANCE.md"
        provenance.write_text(
            provenance.read_text(encoding="utf-8").replace(old_digest, new_digest),
            encoding="utf-8")
        self.remove_manifest_entry("README.md")
        self.refresh_manifest_digest("projection/public-files.txt")
        self.refresh_manifest_digest("PROJECTION-PROVENANCE.md")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("source allowlist", (checked.stdout + checked.stderr).lower())

    def test_self_consistent_payload_tamper_fails_source_binding(self) -> None:
        self.assertEqual(self.run_builder().returncode, 0)
        (self.output / "README.md").write_text("self-consistent tamper\n",
                                                encoding="utf-8")
        self.refresh_manifest_digest("README.md")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("source payload", (checked.stdout + checked.stderr).lower())

    def test_self_consistent_source_identity_tamper_fails(self) -> None:
        self.assertEqual(self.run_builder().returncode, 0)
        provenance = self.output / "PROJECTION-PROVENANCE.md"
        provenance.write_text(
            provenance.read_text(encoding="utf-8").replace(
                "Source commit: `UNAVAILABLE`", "Source commit: `TAMPERED`"),
            encoding="utf-8")
        self.refresh_manifest_digest("PROJECTION-PROVENANCE.md")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("source identity", (checked.stdout + checked.stderr).lower())

    def test_conflicting_source_identity_line_fails(self) -> None:
        self.assertEqual(self.run_builder().returncode, 0)
        provenance = self.output / "PROJECTION-PROVENANCE.md"
        text = provenance.read_text(encoding="utf-8")
        provenance.write_text(
            text.replace("- Source commit time:",
                         "- Source commit: `TAMPERED`\n- Source commit time:", 1),
            encoding="utf-8", newline="\n")
        self.refresh_manifest_digest("PROJECTION-PROVENANCE.md")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("provenance", (checked.stdout + checked.stderr).lower())

    def test_extra_false_identifier_path_fails(self) -> None:
        identifier = "2" * 40
        (self.source / "README.md").write_text(
            f"Private source commit `{identifier}`.\n", encoding="utf-8")
        self.assertEqual(self.run_builder().returncode, 0)
        provenance = self.output / "PROJECTION-PROVENANCE.md"
        text = provenance.read_text(encoding="utf-8")
        provenance.write_text(
            text.replace(f"- `{identifier}` — `README.md`",
                         f"- `{identifier}` — `README.md`, `false/path.md`"),
            encoding="utf-8", newline="\n")
        self.refresh_manifest_digest("PROJECTION-PROVENANCE.md")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("provenance", (checked.stdout + checked.stderr).lower())

    def test_missing_private_input_fails_without_path_or_traceback(self) -> None:
        missing = self.tmp / "missing-private-input.txt"
        built = self.run_builder(patterns=missing)
        build_output = built.stdout + built.stderr
        self.assertNotEqual(built.returncode, 0)
        self.assertNotIn(str(missing), build_output)
        self.assertNotIn("Traceback", build_output)
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker(patterns=missing)
        check_output = checked.stdout + checked.stderr
        self.assertNotEqual(checked.returncode, 0)
        self.assertNotIn(str(missing), check_output)
        self.assertNotIn("Traceback", check_output)

    def test_unknown_file_fails(self) -> None:
        self.assertEqual(self.run_builder().returncode, 0)
        (self.output / "unknown.txt").write_text("unknown\n", encoding="utf-8")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("unknown or missing", (checked.stdout + checked.stderr).lower())

    def test_checker_rejects_injected_symlink(self) -> None:
        self.assertEqual(self.run_builder().returncode, 0)
        target = self.tmp / "outside-check.txt"
        target.write_text("outside\n", encoding="utf-8")
        try:
            (self.output / "linked.txt").symlink_to(target)
        except OSError as exc:
            self.skipTest(f"symlink unavailable: {exc}")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("symlink", (checked.stdout + checked.stderr).lower())

    def test_state_snapshot_boundary_removal_is_rejected(self) -> None:
        """WO-PL-029 B.3.2 item 1.

        Projected `governance/STATE.md` must carry a deterministic note that
        it is a snapshot of the private governed source at the provenance
        source commit, and push/publication/visibility/queued-work
        statements describe that checkpoint rather than the current public
        copy. Historically RED: before this work order the builder added no
        such note and the checker required none, so a candidate with the
        boundary stripped away still passed. Now GREEN: the builder always
        writes the note and the checker rejects its removal.
        """
        self.allow("governance/STATE.md",
                   "# State\n\nQueued work: none.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        projected = self.output / "governance" / "STATE.md"
        text = projected.read_text(encoding="utf-8")
        self.assertIn("snapshot of the private governed source", text)
        stripped = text.replace(
            "snapshot of the private governed source", "an unrelated note")
        projected.write_text(stripped, encoding="utf-8")
        self.refresh_manifest_digest("governance/STATE.md")
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("snapshot", (checked.stdout + checked.stderr).lower())

    def test_unqualified_concrete_omitted_report_reference_fails(self) -> None:
        """WO-PL-029 B.3.2 item 2.

        A concrete `governance/reports/<file>` reference to a report the
        candidate omits must be qualified the same way archive/history/dist
        references are, or the checker must reject it. Historically RED:
        before this work order, `governance/reports/` was not covered by the
        retained-reference pattern, so an unqualified concrete backtick
        reference passed unnoticed. Now GREEN: the checker rejects it.
        """
        self.allow("NOTES.md",
                   "See `governance/reports/WO-PL-099-report.md` for detail.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("retains an unresolved reference",
                      checked.stdout + checked.stderr)

    def test_unqualified_plain_omitted_report_reference_fails(self) -> None:
        """WO-PL-029 fresh Reviewer BLOCK/MEDIUM regression.

        Historically RED: the token matched only backtick-delimited paths, so
        the plain concrete omitted-report reference passed. Now GREEN: the
        checker recognizes and rejects the same path in plain prose.
        """
        self.allow("NOTES.md",
                   "See governance/reports/WO-PL-099-report.md for detail.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("retains an unresolved reference",
                      checked.stdout + checked.stderr)

    def test_unqualified_markdown_link_omitted_report_reference_fails(self) -> None:
        """WO-PL-029 fresh Reviewer BLOCK/MEDIUM regression.

        Historically RED: a concrete omitted report used as a Markdown link
        target passed because the token required backticks. Now GREEN: the
        checker recognizes and rejects that link target.
        """
        self.allow("NOTES.md",
                   "See [the report](governance/reports/WO-PL-099-report.md) "
                   "for detail.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("retains an unresolved reference",
                      checked.stdout + checked.stderr)

    def test_generic_reports_directory_mention_remains_valid(self) -> None:
        """Companion GREEN guard: a bare directory mention with no concrete
        omitted file must stay valid, in backtick, plain, and link form."""
        self.allow("NOTES.md",
                   "Reports live under `governance/reports/` generally, see "
                   "also governance/reports/ and "
                   "[the index](governance/reports/) for more.\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_markdown_link_to_a_present_candidate_file_remains_valid(self) -> None:
        """A report link to a shipped file must remain valid."""
        self.allow("governance/reports/public-report.md", "# Public report\n")
        self.allow("NOTES.md",
                   "See [the report](governance/reports/public-report.md).\n")
        self.assertEqual(self.run_builder().returncode, 0)
        checked = self.run_checker()
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_provenance_omits_private_pattern_digest(self) -> None:
        """WO-PL-029 B.3.2 item 3.

        No value-derived fingerprint of the Owner-private pattern input may
        enter candidate bytes or ordinary output; the private input remains
        mandatory at build/check time only for the local zero-match gate.
        Historically RED: before this work order the builder wrote and the
        checker required a 'Private-pattern input SHA-256' line in
        provenance, which is exactly such a fingerprint. Now GREEN: neither
        writes nor accepts that line.
        """
        self.assertEqual(self.run_builder().returncode, 0)
        provenance = (self.output / "PROJECTION-PROVENANCE.md").read_text(
            encoding="utf-8")
        self.assertNotIn("Private-pattern input SHA-256", provenance)

    def test_two_candidates_are_byte_identical(self) -> None:
        first = self.run_builder(source=REPO_ROOT)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        second_output = self.tmp / "candidate-two"
        second = self.run_builder(source=REPO_ROOT, output=second_output)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        first_files = sorted(path.relative_to(self.output).as_posix()
                             for path in self.output.rglob("*") if path.is_file())
        second_files = sorted(path.relative_to(second_output).as_posix()
                              for path in second_output.rglob("*") if path.is_file())
        self.assertEqual(first_files, second_files)
        for relative in first_files:
            self.assertEqual((self.output / relative).read_bytes(),
                             (second_output / relative).read_bytes(), relative)

    def test_public_root_has_no_active_host_specific_hook_registration(self) -> None:
        built = self.run_builder(source=REPO_ROOT)
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        public_charter = (self.output / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("not Writwall's governed source", public_charter)
        self.assertIn("ordinary repository changes", public_charter)
        self.assertNotIn("No mutation without an active work order", public_charter)
        self.assertFalse((self.output / ".claude" / "settings.json").exists())
        self.assertFalse((self.output / ".claude" / "hooks"
                          / "wo_capability_wall.py").exists())
        self.assertTrue((self.output / "adapters" / "claude-code"
                         / "wo_capability_wall.py").is_file())
        checked = self.run_checker(output=self.output, source=REPO_ROOT)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)


if __name__ == "__main__":
    unittest.main()
