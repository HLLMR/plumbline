# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Tests for the distribution checker and builder.

Standard library only. Each test copies the repository into its own temporary
directory and mutates the copy, so every failure category is observed firing
rather than assumed. Nothing is written outside the fixture directory.
"""
from __future__ import annotations

import hashlib
import json
import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "dist", "__pycache__", ".pytest_cache", "bootstrap"}
IS_PROJECTION = all(
    (REPO_ROOT / name).is_file()
    for name in ("PROJECTION-MANIFEST.sha256", "PROJECTION-PROVENANCE.md")
)


def load_distribution_builder():
    spec = importlib.util.spec_from_file_location(
        "wo_pl_031_build_distribution",
        REPO_ROOT / "scripts" / "build_distribution.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_distribution_checker():
    spec = importlib.util.spec_from_file_location(
        "wo_pl_031_check_distribution",
        REPO_ROOT / "checks" / "check_distribution.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MachinePathBoundaryTests(unittest.TestCase):
    def test_shallow_home_is_not_an_unbounded_prose_substring(self):
        shallow_home = "/" + "root"
        for module in (load_distribution_builder(), load_distribution_checker()):
            with self.subTest(module=module.__name__):
                self.assertFalse(module.machine_path_occurs(
                    "nested/root-relative Markdown targets", shallow_home))
                self.assertTrue(module.machine_path_occurs(
                    "repository: " + shallow_home + "/Projects/example", shallow_home))
                self.assertTrue(module.machine_path_occurs(
                    "home=" + shallow_home, shallow_home))
                self.assertTrue(module.machine_path_occurs(
                    "Home is " + shallow_home + ".", shallow_home))


def pre_adoption_fixture(repo: Path) -> Path:
    """Pin a fixture to the pre-adoption governance state.

    The exact inverse of ``adopt_fixture``. Every fixture is a copy of the real
    tree, so without this the live repository's own lifecycle stage leaks in:
    before Writwall adopted itself the copy was pre-adoption by accident, and
    the moment the Owner signed and renamed the adoption record every
    pre-adoption assertion below began running against an adopted fixture.
    Some failed loudly; others would have passed vacuously, which is worse.

    This is the RFI-12 rule applied to state rather than to filenames: a test
    asserts stable behaviour from a fixture it controls, never from whatever
    stage the live governance instance happens to be in. Tests that want the
    adopted state opt into it explicitly by calling ``adopt_fixture``.
    """
    decisions = repo / "governance" / "decisions"
    if not decisions.is_dir():
        return repo
    (decisions / "DR-001.md").unlink(missing_ok=True)
    (decisions / "DR-001-ADOPTION-PROPOSED.md").write_text(
        "# PROPOSED — Adoption record — NOT RATIFIED, NOT SIGNED\n\n"
        "**Status: PROPOSED.** Never packaged in any release archive.\n\n"
        "Not a real record. It pins this fixture to the pre-adoption state.\n",
        encoding="utf-8", newline="\n")
    # The identity manifest describes the release projection, while this
    # fixture deliberately removes the ratified adoption record. Keep the
    # fixture's own projection inventory and retained-path list coherent rather
    # than making every unrelated pre-adoption test fail on that intentional
    # absence.
    retired_path = "governance/decisions/DR-001.md"
    allowlist = repo / "projection" / "public-files.txt"
    if allowlist.is_file():
        lines = [
            line for line in allowlist.read_text(encoding="utf-8").splitlines()
            if line != retired_path
        ]
        allowlist.write_text(
            "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
        )
    identity_manifest = repo / "identity" / "legacy-references.json"
    if identity_manifest.is_file():
        payload = json.loads(identity_manifest.read_text(encoding="utf-8"))
        payload["retained"] = [
            entry for entry in payload.get("retained", [])
            if entry.get("path") != retired_path
        ]
        identity_manifest.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    return repo


def clear_transient_release_state(repo: Path) -> Path:
    """Pin a copied fixture to a between-work-orders lifecycle state.

    Distribution fixtures describe their own live-work inputs. They must not
    inherit the source repository's active pointer, work order, or report just
    because the suite happens to run during an implementation cycle.
    """
    (repo / ".claude" / "active-wo.txt").unlink(missing_ok=True)
    for live_dir in ("governance/work-orders", "governance/reports"):
        directory = repo / live_dir
        if not directory.is_dir():
            continue
        root_placeholder = f"{live_dir}/.gitkeep"
        for path in directory.rglob("*"):
            if (path.is_file()
                    and path.relative_to(repo).as_posix() != root_placeholder):
                path.unlink()
        for path in sorted(
                (candidate for candidate in directory.rglob("*")
                 if candidate.is_dir()),
                key=lambda candidate: len(candidate.parts), reverse=True):
            if not any(path.iterdir()):
                path.rmdir()
    return repo


def materialize_source_provenance_fixture(repo: Path) -> Path:
    """Supply source-only evidence to tests running from a public projection.

    The projection deliberately excludes the private archive and Git history.
    Most tests still exercise the governed-source checker against isolated
    disposable copies, so they receive the minimum synthetic evidence required
    by those source-mode gates.  The real projection is validated separately
    by ``ProjectionContextTests`` and never gains these paths.
    """
    if not IS_PROJECTION:
        return repo
    archive = repo / "archive"
    proposal = (archive / "proposed-v0.1" / "decisions" /
                "DR-001-PROPOSAL-NEVER-RATIFIED.md")
    proposal.parent.mkdir(parents=True, exist_ok=True)
    proposal.write_text(
        "# PROPOSAL — NEVER RATIFIED — NO AUTHORITY\n\n"
        "**Proposed by:** HLLMR\n\n"
        "**Date:** 2026-08-14\n\n"
        "This fixture records a proposal that was never adopted.\n",
        encoding="utf-8", newline="\n")
    (archive / "README.md").write_text(
        "# Synthetic source-provenance test fixture\n\n"
        "Original path: decisions/DR-001.md\n\n"
        "Baseline: 6e165e585f907baf83a787ba5cc71270a5a4652e\n\n"
        "Blob: 9cf9aa5f188a5351d4c12b53763b4c3c4688ba28efefb57a284a2fcf120e74ab\n\n"
        "The original is recoverable from Git history. Correction: 2026-08-16.\n\n"
        "No byte-for-byte claim is made for the corrected fixture.\n",
        encoding="utf-8", newline="\n")
    return repo


def copy_repo(destination: Path) -> Path:
    shutil.copytree(
        REPO_ROOT, destination,
        ignore=shutil.ignore_patterns(*SKIP_DIRS),
        dirs_exist_ok=True)
    # Exercise the prospective post-install distribution contract only in
    # the disposable fixture; the governed installed control plane in the
    # source repository remains untouched before lifecycle authorization.
    installed = destination / ".claude" / "hooks" / "wo_capability_wall.py"
    installed.parent.mkdir(parents=True, exist_ok=True)
    installed.write_bytes(
        (destination / "adapters" / "claude-code" / "wo_capability_wall.py").read_bytes())
    settings = destination / ".claude" / "settings.json"
    settings.write_text(json.dumps({"hooks": {"PreToolUse": [{
        "matcher": "*",
        "hooks": [{
            "type": "command",
            "command": "py -3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/wo_capability_wall.py\"",
            "timeout": 10,
        }],
    }]}}, indent=2) + "\n", encoding="utf-8", newline="\n")
    materialize_source_provenance_fixture(destination)
    return pre_adoption_fixture(clear_transient_release_state(destination))


class DistributionTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = copy_repo(self.tmp / "writwall")

    def check(self, *extra):
        return subprocess.run(
            [sys.executable, str(self.repo / "checks" / "check_distribution.py"),
             *extra],
            capture_output=True, text=True, timeout=300)

    def build(self, *extra):
        return subprocess.run(
            [sys.executable, str(self.repo / "scripts" / "build_distribution.py"),
             "--output", "dist/", *extra],
            capture_output=True, text=True, timeout=300)

    def assert_fails(self, result, category):
        self.assertNotEqual(result.returncode, 0,
                            f"expected failure, got success:\n{result.stdout}")
        self.assertIn(category, result.stdout,
                      f"expected a [{category}] failure:\n{result.stdout}")

    def edit(self, relative, old, new, count=1):
        path = self.repo / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, f"fixture text not found in {relative}")
        path.write_text(text.replace(old, new) if count == -1
                        else text.replace(old, new, count), encoding="utf-8", newline="\n")

    def set_dc2_ratified(self, value):
        """Rewrite only the DC.2 ratified cell for the current revision, never
        the row's prose, which changes as corrections are recorded."""
        path = self.repo / "DOCTRINE.md"
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        for index, line in enumerate(lines):
            if line.startswith("| 0.8 |"):
                cells = line.rstrip("\r\n").strip("|").split("|")
                cells[-1] = f" {value} "
                lines[index] = "|" + "|".join(cells) + "|\n"
                break
        else:
            self.fail("no DC.2 row for revision 0.8")
        path.write_text("".join(lines), encoding="utf-8", newline="\n")

    def set_dc1_status(self, value):
        path = self.repo / "DOCTRINE.md"
        text = path.read_text(encoding="utf-8")
        new = re.sub(r"^\| Status \| .* \|$", f"| Status | {value} |",
                     text, count=1, flags=re.MULTILINE)
        self.assertNotEqual(new, text, "DC.1 Status row not found")
        path.write_text(new, encoding="utf-8", newline="\n")

    def make_candidate(self):
        """Return the fixture to a pre-ratification candidate state, including
        the artefacts that state requires."""
        self.set_dc1_status("Ratification candidate")
        self.set_dc2_ratified("Pending")
        self.edit("DOCTRINE.md", "*Revision 0.8. Ratified 2026-08-21 by DR-005.",
                  "*Revision 0.8. Ratification candidate.")
        draft = self.repo / "decisions" / "RATIFICATION-RECORD-DRAFT.md"
        draft.write_text("# DRAFT — NO AUTHORITY\n\nRevision 0.8, unsigned.\n",
                         encoding="utf-8", newline="\n")
        (self.repo / "decisions" / "DR-005.md").unlink()
        for name in ("README.md", "ADOPTING.md", "SELF-HOSTING.md", "decisions/README.md"):
            path = self.repo / name
            path.write_text(
                path.read_text(encoding="utf-8")
                    .replace("ratified 2026-08-21", "pending ratification")
                    .replace("Ratified 2026-08-21", "Pending ratification")
                    .replace("ratified on 2026-08-21", "not yet ratified")
                    .replace("ratified Doctrine revision 0.8 on 2026-08-21",
                             "not yet ratified Doctrine revision 0.8")
                    .replace("is the current ratified revision",
                             "is a ratification candidate")
                    .replace("is the current ratified methodology revision",
                             "is a ratification candidate"),
                encoding="utf-8", newline="\n")


class CheckerPassesOnCleanTree(DistributionTestCase):
    def test_clean_copy_passes(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("all distribution checks passed", result.stdout)


class CIWorkflowTests(DistributionTestCase):
    def test_ci_declares_native_os_and_truthful_python_scopes(self):
        workflow = self.repo / ".github" / "workflows" / "ci.yml"
        self.assertTrue(workflow.is_file(), "checked-in CI workflow is missing")
        text = workflow.read_text(encoding="utf-8")
        for required in (
            "ubuntu-latest", "windows-latest", "macos-latest",
            '"3.10"', '"3.11"', '"3.12"', '"3.13"', '"3.14"',
            "tests.test_wo_capability_wall",
            "tests.test_check_work_order_dispatch",
            "tests.test_init_sh",
            "python -B -m unittest discover -s tests",
            "fetch-depth: 0",
            "matrix.python-version != '3.10'",
        ):
            self.assertIn(required, text)
        self.assertIn("contents: read", text)

    def test_ci_provisions_declared_build_requirements_before_tests(self):
        pyproject = (self.repo / "pyproject.toml").read_text(encoding="utf-8")
        build_system = re.search(
            r"(?ms)^\[build-system\]\s*$.*?^requires\s*=\s*\[(.*?)\]",
            pyproject,
        )
        self.assertIsNotNone(build_system, "build-system.requires is missing")
        requirements = re.findall(r'"([^"]+)"', build_system.group(1))
        self.assertTrue(requirements, "build-system.requires is empty")

        workflow = (self.repo / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )
        test_boundary = workflow.index("Focused capability-wall, dispatch, and init tests")
        provisioning = workflow[:test_boundary]
        self.assertIn("Provision declared build backend", provisioning)
        self.assertIn("python -m pip install", provisioning)
        self.assertIn("--no-input", provisioning)
        self.assertIn("--only-binary=:all:", provisioning)
        for requirement in requirements:
            with self.subTest(requirement=requirement):
                self.assertIn(f'"{requirement}"', provisioning)


class CurrentDocumentationSynchronizationTests(unittest.TestCase):
    def test_adapter_readme_lists_every_reason_code_and_surface(self):
        import importlib.util
        adapter_path = REPO_ROOT / "adapters" / "claude-code" / "wo_capability_wall.py"
        spec = importlib.util.spec_from_file_location("_doc_sync_wall", adapter_path)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        readme = (REPO_ROOT / "adapters" / "claude-code" / "README.md").read_text(
            encoding="utf-8")
        for reason_code in adapter.SAFE_REASONS:
            with self.subTest(reason_code=reason_code):
                self.assertIn(f"`{reason_code}`", readme)
        for surface in set(adapter.SURFACE_BY_KIND.values()) | {adapter.SURFACE_UNKNOWN}:
            with self.subTest(surface=surface):
                self.assertIn(f"`{surface}`", readme)

    def test_current_docs_record_the_operational_0_8_project_binding(self):
        for relative in ("README.md", "SELF-HOSTING.md"):
            text = (REPO_ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(path=relative):
                self.assertNotIn("remains bound to 0.6", text)
                self.assertIn("operatively bound to Doctrine 0.8", text)


class CheckerFailureCategories(DistributionTestCase):
    def test_unclassified_former_identity_fails_release_gate(self):
        self.edit(
            "START-HERE.md",
            "Writwall adoption coordinator",
            "Plumbline adoption coordinator",
        )

        result = self.check()
        self.assert_fails(result, "identity")
        self.assertIn(
            "START-HERE.md contains an unclassified former-identity match",
            result.stdout,
        )

    def test_pending_name_clearance_disposition_fails_release_gate(self):
        ledger = (
            self.repo / "examples" / "name-clearance-ledgers" /
            "writwall-candidate.json"
        )
        payload = json.loads(ledger.read_text(encoding="utf-8"))
        payload["disposition"] = {"decision": "pending"}
        ledger.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
        )

        self.assert_fails(self.check(), "name-clearance")

    def test_selected_name_disposition_is_pinned_for_release(self):
        ledger = (
            self.repo / "examples" / "name-clearance-ledgers" /
            "writwall-candidate.json"
        )
        payload = json.loads(ledger.read_text(encoding="utf-8"))
        payload["disposition"]["decision"] = "reject"
        payload["disposition"]["rationale"] = "Mutated release decision."
        ledger.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
        )

        result = self.check()

        self.assert_fails(result, "name-clearance")
        self.assertIn("writwall-candidate.json must record Writwall accept", result.stdout)

    def test_owner_human_review_attestation_is_pinned_for_release(self):
        ledger = (
            self.repo / "examples" / "name-clearance-ledgers" /
            "writwall-candidate.json"
        )
        payload = json.loads(ledger.read_text(encoding="utf-8"))
        human_source = next(
            source for source in payload["sources"]
            if source["id"] == "web_common_law"
        )
        human_source["reviewed_by"] = "Codex"
        ledger.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n"
        )

        result = self.check()

        self.assert_fails(result, "name-clearance")
        self.assertIn("must retain HLLMR, Owner human review", result.stdout)

    def test_missing_required_file_fails(self):
        (self.repo / "templates" / "A-charter.md").unlink()
        self.assert_fails(self.check(), "required-file")

    def test_missing_ci_workflow_fails_required_file(self):
        (self.repo / ".github" / "workflows" / "ci.yml").unlink()
        result = self.check()
        self.assert_fails(result, "required-file")
        self.assertIn(".github/workflows/ci.yml", result.stdout)

    def test_missing_dr005_fails_required_file(self):
        (self.repo / "decisions" / "DR-005.md").unlink()
        result = self.check()
        self.assert_fails(result, "required-file")
        self.assertIn("decisions/DR-005.md", result.stdout)

    def test_drifted_skill_bundle_copy_fails(self):
        path = self.repo / "skills" / "writwall-adopt" / "references" / "DOCTRINE.md"
        path.write_text(path.read_text(encoding="utf-8") + "\ndrift\n", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "bundle")

    def test_missing_skill_bundle_copy_fails(self):
        (self.repo / "skills" / "writwall-adopt" / "assets" / "templates" /
         "C-owner-brief.md").unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("bundle" in result.stdout or "required-file" in result.stdout)

    def test_template_body_drift_fails(self):
        self.edit("templates/B-work-order.md",
                  "## B.2 OBJECTIVE", "## B.2 OBJECTIVE (locally reworded)")
        self.assert_fails(self.check(), "template")

    def test_template_heading_drift_fails(self):
        self.edit("templates/C-owner-brief.md",
                  "# Doctrine Appendix C.", "# Appendix C.")
        self.assert_fails(self.check(), "template")

    def test_stale_qualification_reference_in_doctrine_fails(self):
        self.edit("DOCTRINE.md",
                  "empirical instrument and its qualification status under 8.4.4.",
                  "empirical instrument and its qualification status under 8.4.3.")
        self.assert_fails(self.check(), "qualification")

    def test_stale_qualification_reference_in_metric_row_fails(self):
        self.edit("DOCTRINE.md",
                  "feeds a later qualification event under 8.4.4",
                  "feeds qualification under 8.4.3")
        self.assert_fails(self.check(), "qualification")

    def test_stale_qualification_reference_in_template_fails(self):
        self.edit("templates/D-adoption-record.md",
                  "qualification status under 8.4.4.",
                  "qualification status under 8.4.3.")
        result = self.check()
        self.assert_fails(result, "qualification")

    def test_dc1_ratified_but_dc2_pending_fails(self):
        self.set_dc2_ratified("Pending")
        self.assert_fails(self.check(), "markers")

    def test_dc2_ratified_but_dc1_candidate_fails(self):
        self.set_dc1_status("Ratification candidate")
        self.assert_fails(self.check(), "markers")

    def test_missing_ratification_record_while_ratified_fails(self):
        (self.repo / "decisions" / "DR-005.md").unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("markers" in result.stdout or "required-file" in result.stdout)

    def test_ratification_record_still_carrying_draft_marker_fails(self):
        path = self.repo / "decisions" / "DR-005.md"
        path.write_text("# DRAFT — NO AUTHORITY\n\nRevision ratified | 0.8\n",
                        encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "markers")


class DoctrineRatificationTests(DistributionTestCase):
    def test_current_revision_resolves_to_dr005_ratified_0_8(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("doctrine revision 0.8", result.stdout)
        self.assertIn("DC.1 status 'Ratified'", result.stdout)
        bundled = (self.repo / "skills" / "writwall-adopt" / "references" /
                   "DOCTRINE.md").read_bytes()
        canonical = (self.repo / "DOCTRINE.md").read_bytes()
        self.assertEqual(bundled, canonical)

    def test_second_dr_row_claiming_0_8_ratified_is_ambiguous_and_fails(self):
        """resolve_ratification_record is fail-closed: exactly one decisions/
        DR-*.md record may name '| Revision ratified | 0.8 |'. A second one
        makes the ratification record ambiguous rather than picked by name."""
        duplicate = self.repo / "decisions" / "DR-006.md"
        duplicate.write_text(
            "# DR-006: Duplicate ratification claim (fixture)\n\n"
            "| Field | Value |\n"
            "|---|---|\n"
            "| Record | DR-006, methodology-source decision |\n"
            "| Owner | HLLMR |\n"
            "| Date | 2026-08-21 |\n"
            "| Revision ratified | 0.8 |\n"
            "| Supersedes | 0.7 |\n",
            encoding="utf-8", newline="\n")
        result = self.check()
        self.assert_fails(result, "markers")
        self.assertIn("found 2", result.stdout)


class MigrationGuideZeroSevenTests(DistributionTestCase):
    def test_bundled_0_6_to_0_7_guide_exists_matches_and_drift_fails(self):
        canonical = self.repo / "migration-guides" / "0.6-to-0.7.md"
        bundled = (self.repo / "skills" / "writwall-adopt" / "references" /
                   "migration-guides" / "0.6-to-0.7.md")
        self.assertTrue(canonical.is_file(),
                        "migration-guides/0.6-to-0.7.md does not exist")
        self.assertTrue(bundled.is_file(),
                        "skills/writwall-adopt/references/migration-guides/"
                        "0.6-to-0.7.md does not exist")
        self.assertEqual(bundled.read_bytes(), canonical.read_bytes())

        bundled.write_text(
            bundled.read_text(encoding="utf-8") + "\ndrift\n",
            encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "bundle")

    def test_footer_still_calling_it_a_candidate_fails(self):
        self.edit("DOCTRINE.md", "*Revision 0.8. Ratified 2026-08-21 by DR-005.",
                  "*Revision 0.8. Ratification candidate.")
        self.assert_fails(self.check(), "markers")

    def test_readme_still_calling_it_a_candidate_fails(self):
        readme = self.repo / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") +
                          "\nRevision 0.6 is a ratification candidate.\n", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "markers")

    def test_ratified_claim_while_candidate_fails(self):
        self.make_candidate()
        readme = self.repo / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") +
                          "\nThis is the ratified revision 0.8.\n", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "markers")

    def test_missing_ratification_draft_fails_while_candidate(self):
        self.make_candidate()
        (self.repo / "decisions" / "RATIFICATION-RECORD-DRAFT.md").unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("markers" in result.stdout or "required-file" in result.stdout)

    def test_forbidden_mnt_user_data_tree_fails(self):
        target = self.repo / "mnt" / "user-data" / "outputs"
        target.mkdir(parents=True)
        (target / "stray.md").write_text("x", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "forbidden-path")

    def test_loose_alternate_filenames_fail(self):
        for name in ("DOCTRINE_v0.6.md", "wo_capability_wall_v06.py",
                     "REMEDIATION_COMPANION_0.1_to_0.6.md"):
            with self.subTest(name=name):
                stray = self.repo / name
                stray.write_text("x", encoding="utf-8", newline="\n")
                self.assert_fails(self.check(), "forbidden-path")
                stray.unlink()

    def test_nested_zip_fails(self):
        nested = self.repo / "bundle.zip"
        with zipfile.ZipFile(nested, "w") as archive:
            archive.writestr("a.txt", "a")
        self.assert_fails(self.check(), "forbidden-path")

    def test_adapter_coverage_disagreement_fails(self):
        self.edit("adapters/claude-code/wo_capability_wall.py",
                  '    "Write",\n})', '    "Write",\n    "FutureWriter",\n})')
        self.assert_fails(self.check(), "coverage")

    def test_readme_coverage_disagreement_fails(self):
        self.edit("adapters/claude-code/README.md",
                  "SHELL_TOOLS = Bash, KillShell, Monitor, PowerShell",
                  "SHELL_TOOLS = Bash, KillShell, Monitor")
        self.assert_fails(self.check(), "coverage")

    def test_archived_v01_tree_is_exempt_from_forbidden_scan(self):
        target = self.repo / "archive" / "proposed-v0.1" / "mnt" / "user-data"
        target.mkdir(parents=True)
        (target / "historical.md").write_text("x", encoding="utf-8", newline="\n")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)


class SelfHostingSegregationTests(DistributionTestCase):
    """Doctrine 5.1.5: Writwall's working records never reach an adopter."""

    def bundle(self):
        return self.repo / "skills" / "writwall-adopt"

    def test_charter_inside_the_bundle_fails(self):
        (self.bundle() / "references" / "CLAUDE.md").write_text("x", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "segregation")

    def test_self_hosting_doc_inside_the_bundle_fails(self):
        (self.bundle() / "assets" / "SELF-HOSTING.md").write_text("x", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "segregation")

    def test_governance_directory_inside_the_bundle_fails(self):
        target = self.bundle() / "assets" / "governance"
        target.mkdir(parents=True)
        (target / "notes.md").write_text("x", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "segregation")

    def test_decisions_directory_inside_the_bundle_fails(self):
        target = self.bundle() / "references" / "decisions"
        target.mkdir(parents=True)
        (target / "DR-002.md").write_text("x", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "segregation")

    def test_plan_state_routing_inside_the_bundle_fail(self):
        for name in ("PLAN.md", "STATE.md", "ROUTING.md", "LOG.md"):
            with self.subTest(name=name):
                stray = self.bundle() / "assets" / name
                stray.write_text("x", encoding="utf-8", newline="\n")
                self.assert_fails(self.check(), "segregation")
                stray.unlink()

    def test_unrecognized_file_in_the_bundle_fails(self):
        (self.bundle() / "assets" / "extra-notes.md").write_text("x", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "segregation")

    def test_clean_bundle_carries_only_skill_and_declared_copies(self):
        files = sorted(p.relative_to(self.bundle()).as_posix()
                       for p in self.bundle().rglob("*") if p.is_file())
        self.assertEqual(files, [
            "LICENSE-MAP.md",
            "SKILL.md",
            "assets/adapters/claude-code/README.md",
            "assets/adapters/claude-code/wo_capability_wall.py",
            "assets/checks/check_name_clearance.py",
            "assets/checks/check_work_order_dispatch.py",
            "assets/scripts/collect_name_clearance.py",
            "assets/templates/A-charter.md",
            "assets/templates/B-work-order.md",
            "assets/templates/C-owner-brief.md",
            "assets/templates/D-adoption-record.md",
            "assets/templates/E-adoption-mapping.md",
            "references/DOCTRINE.md",
            "references/migration-guides/0.1-to-0.6.md",
            "references/migration-guides/0.6-to-0.7.md",
            "references/migration-guides/0.7-to-0.8.md",
            "references/name-clearance.md",
        ])


class PositioningTests(DistributionTestCase):
    """WO-PL-002 items 5.1 and 5.2."""

    CANONICAL = ("Writwall is a document-controlled governance methodology with a "
                 "self-hosting reference implementation and project-scaffolding toolkit.")

    def test_canonical_description_present_verbatim(self):
        collapsed = " ".join((self.repo / "README.md").read_text(encoding="utf-8").split())
        self.assertIn(self.CANONICAL, collapsed)

    def test_missing_canonical_description_fails(self):
        self.edit("README.md", self.CANONICAL, "Writwall is a governance thing.")
        self.assert_fails(self.check(), "positioning")

    def test_missing_source_distribution_phrase_in_readme_fails(self):
        self.edit("README.md", "source distribution, not an overlay",
                  "a package you can unpack anywhere")
        self.assert_fails(self.check(), "positioning")

    def test_missing_source_distribution_phrase_in_adopting_fails(self):
        self.edit("ADOPTING.md", "source distribution, not an overlay",
                  "a package you can unpack anywhere")
        self.assert_fails(self.check(), "positioning")

    def test_doctrine_carries_the_self_hosting_clauses(self):
        text = (self.repo / "DOCTRINE.md").read_text(encoding="utf-8")
        for clause in ("5.1.4 Self-hosting.", "5.1.5 Segregation of the self-hosted instance.",
                       "5.1.6 Self-hosting creates no dependency."):
            self.assertIn(clause, text)
        self.assertIn("### 5.1 Repository Roles", text)

    def test_dc2_records_the_pre_ratification_corrections(self):
        text = (self.repo / "DOCTRINE.md").read_text(encoding="utf-8")
        row = next(l for l in text.splitlines() if l.startswith("| 0.6 |"))
        for fragment in ("1.2.2-1.2.4", "5.1.3", "5.1.4-5.1.6", "A.3", "8.4.4",
                         "1.2.4", "5.1.2"):
            self.assertIn(fragment, row)
        self.assertTrue(row.rstrip().endswith("| Yes |"),
                        "DC.2 ratified column must record ratification")


class CharterRetentionTests(DistributionTestCase):
    """RFI-05 resolution: root CLAUDE.md stays in the source distribution."""

    def test_archive_retains_root_charter(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        archive = next((self.repo / "dist").glob("*.zip"))
        with zipfile.ZipFile(archive) as handle:
            self.assertIn("writwall/CLAUDE.md", handle.namelist())

    def test_archive_without_charter_fails_the_check(self):
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        path = out / "writwall-0.6-rc.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
        self.assert_fails(self.check("--archive", "dist/writwall-0.6-rc.zip"), "archive")

    def test_missing_charter_in_repo_fails(self):
        (self.repo / "CLAUDE.md").unlink()
        self.assert_fails(self.check(), "required-file")


class LineEndingTests(DistributionTestCase):
    """WO-PL-002 item 4.3: conversion cannot silently invalidate equality."""

    def test_crlf_in_a_bundle_copy_fails_loudly_and_names_the_cause(self):
        path = self.repo / "skills" / "writwall-adopt" / "references" / "DOCTRINE.md"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        result = self.check()
        self.assert_fails(result, "bundle")
        self.assertIn("line endings only", result.stdout)

    def test_crlf_in_a_canonical_file_fails_loudly(self):
        path = self.repo / "templates" / "A-charter.md"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        result = self.check()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue("bundle" in result.stdout or "template" in result.stdout)

    def test_crlf_never_reaches_the_manifest(self):
        """Superseded behaviour, recorded deliberately.

        This test previously asserted that the manifest hashed CRLF bytes
        faithfully. Under the Owner disposition of 2026-08-16 a CRLF working
        tree can no longer reach the manifest at all: the build refuses first.
        Refusing is strictly stronger than hashing the damage accurately.
        """
        import hashlib
        readme = self.repo / "README.md"
        crlf = readme.read_bytes().replace(b"\n", b"\r\n")
        readme.write_bytes(crlf)

        result = self.build()
        self.assertNotEqual(result.returncode, 0,
                            "a CRLF working tree produced a release hash")
        self.assertIn("CRLF", result.stderr + result.stdout)
        self.assertEqual(list((self.repo / "dist").glob("*.zip")), [],
                         "an archive was written despite the CRLF preflight")

        # And once corrected, the manifest hashes exactly the on-disk bytes.
        lf = crlf.replace(b"\r\n", b"\n")
        readme.write_bytes(lf)
        self.assertEqual(self.build().returncode, 0)
        archive = next((self.repo / "dist").glob("*.zip"))
        with zipfile.ZipFile(archive) as handle:
            stored = handle.read("writwall/README.md")
            manifest = handle.read("writwall/MANIFEST.sha256").decode("utf-8")
        digests = {rel: dig for dig, _, rel in
                   (line.partition("  ") for line in manifest.splitlines())}
        self.assertEqual(stored, lf)
        self.assertEqual(digests["README.md"], hashlib.sha256(lf).hexdigest())


class GitAttributesTests(unittest.TestCase):
    """Prove .gitattributes takes effect, rather than asserting its text.

    Read-only: runs git check-attr against the real repository and writes
    nothing.
    """

    def check_attr(self, *args):
        if IS_PROJECTION:
            text = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")
            self.assertIn("* text=auto eol=lf", text)
            self.assertIn("*.sh text eol=lf", text)
            self.assertIn("*.zip binary", text)
            self.assertIn("*.png binary", text)
            paths = args[args.index("--") + 1:]
            attributes = args[:args.index("--")]
            parsed = {}
            for path in paths:
                values = {}
                for attribute in attributes:
                    if attribute == "text":
                        values[attribute] = (
                            "unset" if Path(path).suffix in {".zip", ".png"}
                            else "set" if Path(path).suffix == ".sh" else "auto")
                    elif attribute == "eol":
                        values[attribute] = "lf"
                parsed[path] = values
            return parsed
        result = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "check-attr", *args],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        parsed = {}
        for line in result.stdout.splitlines():
            path, _, rest = line.partition(": ")
            attr, _, value = rest.partition(": ")
            parsed.setdefault(path, {})[attr] = value
        return parsed

    def test_gitattributes_exists(self):
        self.assertTrue((REPO_ROOT / ".gitattributes").is_file())

    def test_shell_scripts_are_lf(self):
        attrs = self.check_attr("text", "eol", "--", "init.sh")
        self.assertEqual(attrs["init.sh"]["text"], "set")
        self.assertEqual(attrs["init.sh"]["eol"], "lf")

    def test_text_files_are_lf(self):
        attrs = self.check_attr("text", "eol", "--", "DOCTRINE.md", "README.md",
                                "checks/check_distribution.py")
        for path in ("DOCTRINE.md", "README.md", "checks/check_distribution.py"):
            self.assertEqual(attrs[path]["eol"], "lf", path)
            self.assertIn(attrs[path]["text"], ("auto", "set"), path)

    def test_binaries_are_not_converted(self):
        attrs = self.check_attr("text", "--", "dist/writwall.zip", "img/x.png")
        self.assertEqual(attrs["dist/writwall.zip"]["text"], "unset")
        self.assertEqual(attrs["img/x.png"]["text"], "unset")


class V01DeterminationTests(DistributionTestCase):
    """DR-001: v0.1 was proposed only and never ratified."""

    PROPOSAL = ("archive/proposed-v0.1/decisions/"
                "DR-001-PROPOSAL-NEVER-RATIFIED.md")

    def test_v01_cannot_be_mistaken_for_ratified(self):
        text = (self.repo / self.PROPOSAL).read_text(encoding="utf-8")
        self.assertIn("PROPOSAL — NEVER RATIFIED — NO AUTHORITY", text)
        self.assertIn("Proposed by:** HLLMR", text)
        self.assertIn("2026-08-14", text)
        self.assertIn("never adopted", text.lower().replace("never adopted or made effective",
                                                            "never adopted"))
        self.assertNotRegex(text, r"(?m)^\s*\*\*Ratified by:")

    def test_dc2_records_v01_as_never_ratified(self):
        row = next(l for l in (self.repo / "DOCTRINE.md")
                   .read_text(encoding="utf-8").splitlines() if l.startswith("| 0.1 |"))
        self.assertTrue(row.rstrip().endswith("| No |"), row)

    def test_proposal_missing_marker_fails(self):
        path = self.repo / self.PROPOSAL
        path.write_text(path.read_text(encoding="utf-8")
                        .replace("PROPOSAL — NEVER RATIFIED — NO AUTHORITY", "DR-001"),
                        encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "v0.1")

    def test_reinstated_ratified_by_metadata_fails(self):
        path = self.repo / self.PROPOSAL
        path.write_text("**Ratified by:** HLLMR\n" + path.read_text(encoding="utf-8"),
                        encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "v0.1")

    def test_dc2_claiming_v01_ratified_fails(self):
        doctrine = self.repo / "DOCTRINE.md"
        lines = doctrine.read_text(encoding="utf-8").splitlines(keepends=True)
        for index, line in enumerate(lines):
            if line.startswith("| 0.1 |"):
                cells = line.rstrip("\r\n").strip("|").split("|")
                cells[-1] = " Yes "
                lines[index] = "|" + "|".join(cells) + "|\n"
                break
        doctrine.write_text("".join(lines), encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "v0.1")

    def test_no_current_document_treats_v01_as_authoritative(self):
        for name in ("README.md", "ADOPTING.md", "SELF-HOSTING.md",
                     "DOCTRINE.md", "decisions/README.md", "decisions/DR-001.md"):
            lowered = (self.repo / name).read_text(encoding="utf-8").lower()
            for phrase in ("v0.1 was ratified", "ratified charter v0.1",
                           "ratified revision 0.1"):
                self.assertNotIn(phrase, lowered, f"{name}: {phrase}")

    def test_claiming_v01_authority_fails(self):
        readme = self.repo / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") +
                          "\nNote: v0.1 was ratified in August.\n", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "v0.1")

    def test_stale_archive_path_reference_fails(self):
        readme = self.repo / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") +
                          "\nSee archive/unresolved-v0.1/ for history.\n", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "v0.1")

    def test_old_archive_directory_name_fails(self):
        (self.repo / "archive" / "unresolved-v0.1").mkdir(parents=True)
        self.assert_fails(self.check(), "v0.1")

    def test_historical_reports_are_not_rewritten(self):
        """The reports recorded what was true when written. They still say
        'unresolved-v0.1', and the checker must not force that to change."""
        for name in ("REMEDIATION-REPORT.md", "REMEDIATION-REPORT-WO-PL-002.md"):
            path = self.repo / name
            if path.is_file():
                self.assertIn("unresolved-v0.1", path.read_text(encoding="utf-8"), name)
        self.assertEqual(self.check().returncode, 0)


class ArchiveProvenanceTests(DistributionTestCase):
    BLOB = "9cf9aa5f188a5351d4c12b53763b4c3c4688ba28efefb57a284a2fcf120e74ab"
    BASELINE = "6e165e585f907baf83a787ba5cc71270a5a4652e"

    def test_provenance_recorded(self):
        text = (self.repo / "archive" / "README.md").read_text(encoding="utf-8")
        for needle in (self.BLOB, self.BASELINE, "decisions/DR-001.md",
                       "recoverable from Git history", "2026-08-16"):
            self.assertIn(needle, text)

    def test_no_byte_for_byte_claim_for_the_corrected_file(self):
        text = (self.repo / "archive" / "README.md").read_text(encoding="utf-8")
        self.assertIn("No byte-for-byte claim", text)

    def test_missing_blob_hash_fails(self):
        self.edit("archive/README.md", self.BLOB, "unknown", count=-1)
        self.assert_fails(self.check(), "provenance")

    def test_missing_baseline_commit_fails(self):
        self.edit("archive/README.md", self.BASELINE, "unknown", count=-1)
        self.assert_fails(self.check(), "provenance")

    def test_missing_recoverability_statement_fails(self):
        self.edit("archive/README.md", "recoverable from Git history",
                  "gone forever")
        self.assert_fails(self.check(), "provenance")

    @unittest.skipIf(
        IS_PROJECTION,
        "private Git object retrieval is replaced by projection provenance")
    def test_original_blob_still_retrievable_from_git(self):
        """The provenance claim is only worth what the repository can produce."""
        import hashlib
        blob = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "show",
             f"{self.BASELINE}:decisions/DR-001.md"],
            capture_output=True, timeout=120)
        self.assertEqual(blob.returncode, 0, blob.stderr)
        self.assertEqual(hashlib.sha256(blob.stdout).hexdigest(), self.BLOB)


class ProjectionContextTests(unittest.TestCase):
    """A public projection proves its replacement provenance explicitly.

    These tests run in both contexts.  They prevent the private-only source
    tests above from becoming a silent coverage deletion in a history-free
    public tree.
    """

    def test_projection_context_is_explicit_and_self_consistent(self):
        if not IS_PROJECTION:
            self.assertTrue((REPO_ROOT / "archive" / "README.md").is_file())
            self.assertFalse((REPO_ROOT / "PROJECTION-MANIFEST.sha256").exists())
            return

        self.assertFalse((REPO_ROOT / "archive").exists())
        self.assertFalse((REPO_ROOT / "governance" / "history").exists())
        self.assertTrue((REPO_ROOT / "projection" / "public-files.txt").is_file())
        provenance = (REPO_ROOT / "PROJECTION-PROVENANCE.md").read_text(
            encoding="utf-8")
        self.assertIn("- Source commit:", provenance)
        self.assertIn("- Source commit time:", provenance)
        self.assertIn("- Projection allowlist SHA-256:", provenance)
        self.assertNotIn("Private-pattern input SHA-256", provenance)
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "checks" / "check_distribution.py"),
             "--projection"],
            capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_projection_provenance_with_fingerprint_fails_the_distribution_check(self):
        """RED/GREEN regression for the removed private-pattern fingerprint.

        A candidate whose provenance still discloses a value-derived
        fingerprint of the private pattern input must fail the integrated
        distribution projection gate. Uses a disposable copy, never the
        live source or projection tree.
        """
        if not IS_PROJECTION:
            self.skipTest("only meaningful against a public projection tree")
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        repo = copy_repo(tmp / "writwall")
        provenance = repo / "PROJECTION-PROVENANCE.md"
        original = provenance.read_text(encoding="utf-8")
        tampered = original.replace(
            "## Legacy identifier inventory",
            "- Private-pattern input SHA-256: `" + "0" * 64 + "`\n\n"
            "## Legacy identifier inventory",
            1)
        self.assertNotEqual(tampered, original,
                            "fixture did not locate the inventory heading")
        provenance.write_text(tampered, encoding="utf-8", newline="\n")
        result = subprocess.run(
            [sys.executable, str(repo / "checks" / "check_distribution.py"),
             "--projection"],
            capture_output=True, text=True, timeout=300)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("projection", result.stdout)
        self.assertIn("fingerprint", result.stdout)


class PublicFrontDoorTests(unittest.TestCase):
    """The public README must lead with an executable, honest on-ramp."""

    def test_readme_banner_and_repository_chrome_are_release_ready(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        banner_match = re.search(
            r'src="(docs/assets/writwall-readme-banner-([0-9a-f]{8})\.png)"',
            readme,
        )
        self.assertIsNotNone(
            banner_match,
            "README banner must use a content-versioned public URL",
        )
        banner_path = REPO_ROOT / banner_match.group(1)
        banner = banner_path.read_bytes()
        banner_svg = (REPO_ROOT / "docs" / "assets" /
                      "writwall-readme-banner.svg").read_text(encoding="utf-8")
        social = (REPO_ROOT / "docs" / "assets" / "writwall-og.png").read_bytes()
        social_svg = (REPO_ROOT / "docs" / "assets" /
                      "writwall-og.svg").read_text(encoding="utf-8")

        self.assertLess(len(banner), 500 * 1024)
        self.assertEqual(banner[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(
            (int.from_bytes(banner[16:20], "big"),
             int.from_bytes(banner[20:24], "big")),
            (1280, 320),
        )
        self.assertEqual(social[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(
            (int.from_bytes(social[16:20], "big"),
             int.from_bytes(social[20:24], "big")),
            (1280, 640),
        )
        self.assertEqual(
            banner_match.group(2),
            hashlib.sha256(banner).hexdigest()[:8],
            "README banner filename must match its SHA-256 prefix",
        )
        self.assertFalse(
            (REPO_ROOT / "docs" / "assets" /
             "writwall-readme-banner.png").exists(),
            "the cache-unsafe unversioned public banner must be absent",
        )
        self.assertIn('alt="Writwall: document-governed AI work', readme)
        self.assertIn('width="720"', readme)
        self.assertIn('viewBox="0 0 1280 320"', banner_svg)
        self.assertIn(
            "Document-governed AI work: written authority, bounded capability, retained evidence.",
            banner_svg,
        )
        self.assertIn(
            '<line x1="248.36" y1="126.36" x2="248.36" y2="175.00"',
            banner_svg,
        )
        self.assertIn(
            '<line x1="254.44" y1="126.36" x2="254.44" y2="175.00"',
            banner_svg,
        )
        self.assertNotIn("<circle", banner_svg)
        self.assertNotIn("A wall nobody has watched", banner_svg)
        self.assertIn('viewBox="0 0 1280 640"', social_svg)
        self.assertIn("Governance for AI-assisted", social_svg)
        self.assertIn(
            "Written authority before action. Bounded capability during it.",
            social_svg,
        )
        self.assertIn(
            "Retained evidence before acceptance. The pilot log ships, failing rows and all.",
            social_svg,
        )
        self.assertIn(
            '<line x1="183.63" y1="97.60" x2="183.63" y2="128.00"',
            social_svg,
        )
        self.assertIn(
            '<line x1="187.43" y1="97.60" x2="187.43" y2="128.00"',
            social_svg,
        )
        self.assertNotIn("<circle", social_svg)
        self.assertLess(readme.index("<img"), readme.index(
            '<h1 align="center">Writwall</h1>'))
        for chrome in (
                "actions/workflows/ci.yml/badge.svg",
                "img.shields.io/github/v/release/HLLMR/writwall",
                "doctrine-0.8",
                "security-policy",
                'href="#try-it-in-five-minutes">Five-minute start</a>',
                'href="#how-writwall-differs">How it differs</a>',
                'href="LICENSE-MAP.md">License map</a>'):
            self.assertIn(chrome, readme)

    def test_readme_uses_real_denial_evidence_for_the_sixty_second_mechanism(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        section = readme[readme.index("## See the mechanism in 60 seconds"):]
        section = section[:section.index("\n## ", 3)]
        for truth in (
                "WO-PL-033",
                "`.git/config`",
                "`control_plane_channel_uninspectable`",
                "`write_target_out_of_grant`",
                "No denied mutation succeeded",
                "authorized coordinator"):
            self.assertIn(truth, section)

    def test_banner_is_public_allowlisted_and_license_mapped(self):
        relatives = {
            "docs/assets/writwall-og.png",
            "docs/assets/writwall-og.svg",
            "docs/assets/writwall-readme-banner-0a5259d8.png",
            "docs/assets/writwall-readme-banner.svg",
        }
        allowlist = (REPO_ROOT / "projection" / "public-files.txt").read_text(
            encoding="utf-8").splitlines()
        reuse = (REPO_ROOT / "REUSE.toml").read_text(encoding="utf-8")
        license_map = (REPO_ROOT / "LICENSE-MAP.md").read_text(encoding="utf-8")

        self.assertTrue(relatives.issubset(set(allowlist)))
        self.assertNotIn("docs/assets/writwall-readme-banner.png", allowlist)
        self.assertIn('"docs/assets/**"', reuse)
        self.assertIn("`docs/assets/**`", license_map)

    def test_repository_automation_is_pinned_and_maintainable(self):
        workflow = (REPO_ROOT / ".github" / "workflows" /
                    "ci.yml").read_text(encoding="utf-8")
        dependabot = (REPO_ROOT / ".github" /
                      "dependabot.yml").read_text(encoding="utf-8")
        security = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")

        self.assertRegex(
            workflow,
            r"(?m)uses: actions/checkout@[0-9a-f]{40}  # v4$",
        )
        self.assertRegex(
            workflow,
            r"(?m)uses: actions/setup-python@[0-9a-f]{40}  # v5$",
        )
        self.assertIn("required:", workflow)
        self.assertIn("name: CI required", workflow)
        self.assertIn("needs: test", workflow)
        self.assertIn('package-ecosystem: "github-actions"', dependabot)
        self.assertIn("interval: weekly", dependabot)
        self.assertIn("private vulnerability report", security.lower())

    def test_first_value_sections_precede_repository_taxonomy(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        headings = [
            "## The problem",
            "## The four-step loop",
            "## Try it in five minutes",
            "## What the pilot showed",
            "## How Writwall differs",
            "## Enforcement boundary",
            "## What is in this repository",
        ]
        positions = [readme.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))

        front_door = " ".join(readme[:positions[-1]].split())
        for truth in (
                "one self-hosting pilot",
                "Claude Code",
                "instruction-bounded",
                "governs AI-assisted development",
                "what the installed adapter actually blocked",
                "Spec-driven tools",
                "does not register, activate, or birth-test",
                "19 rework cycles",
                "0 successful out-of-grant mutations"):
            self.assertIn(truth, front_door)

    def test_human_start_ramp_names_roles_interfaces_and_first_prompts(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        start = (REPO_ROOT / "START-HERE.md").read_text(encoding="utf-8")
        adopting = (REPO_ROOT / "ADOPTING.md").read_text(encoding="utf-8")

        self.assertIn('href="START-HERE.md">Start here</a>', readme)
        self.assertLess(readme.index('href="START-HERE.md">Start here</a>'),
                        readme.index('href="ADOPTING.md">Adopt</a>'))
        self.assertIn("does not register, activate, or birth-test", readme)
        for truth in (
                "Small project",
                "Split-role",
                "Provider-neutral",
                "adoption coordinator",
                "walled Implementer",
                "fresh Reviewer",
                "Act as my Writwall adoption coordinator",
                "already-installed lockout",
                "accidental-overlay recovery coordinator",
                "recorder closeout",
                "one question at a time",
                "chat exchange alone is not lifecycle authorization"):
            self.assertIn(truth, start)
        self.assertIn("START-HERE.md", adopting)
        self.assertIn("both doctrinal birth-test levels", adopting)
        self.assertIn("does not by itself block adoption", adopting)
        self.assertIn("durable lifecycle authorization", adopting)

    def test_bootstrap_guidance_is_local_first_and_external_probe_safe(self):
        adopting = (REPO_ROOT / "ADOPTING.md").read_text(encoding="utf-8")
        skill = (REPO_ROOT / "skills" / "writwall-adopt" /
                 "SKILL.md").read_text(encoding="utf-8")
        adapter = (REPO_ROOT / "adapters" / "claude-code" /
                   "README.md").read_text(encoding="utf-8")
        combined = "\n".join((adopting, skill, adapter)).lower()

        for truth in (
                "before the wall is registered",
                "minimal provider profile",
                "explicit disposable",
                "indeterminate, never a pass",
                "re-establish the no-pointer state"):
            self.assertIn(truth, combined)
        self.assertIn(
            "unplanned denials are not retroactively promoted into a birth test",
            combined,
        )
        self.assertIn("portable windows-and-posix claim", combined)

    def test_public_contribution_workflow_is_agent_routable(self):
        required = (
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/pull_request_template.md",
            "docs/agents/issue-tracker.md",
            "docs/agents/triage-labels.md",
            "docs/agents/domain.md",
        )
        for relative in required:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)

    def test_inception_name_clearance_gate_is_public_and_evidence_backed(self):
        required = {
            "checks/check_name_clearance.py",
            "scripts/collect_name_clearance.py",
            "tests/test_name_clearance.py",
            "docs/name-clearance.md",
            "examples/name-clearance-incident-2026-08.md",
            "examples/name-clearance-ledgers/plumbline-incident.json",
            "examples/name-clearance-ledgers/writwall-candidate.json",
            "examples/name-clearance-ledgers/grantcord-candidate.json",
            "examples/name-clearance-ledgers/writcord-candidate.json",
        }
        allowlist = set(
            (REPO_ROOT / "projection" / "public-files.txt").read_text(
                encoding="utf-8"
            ).splitlines()
        )
        self.assertTrue(required.issubset(allowlist))
        reuse = (REPO_ROOT / "REUSE.toml").read_text(encoding="utf-8")
        self.assertIn('"docs/name-clearance.md"', reuse)
        for relative in required:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)

        for relative in ("README.md", "START-HERE.md", "CONTRIBUTING.md"):
            text = (REPO_ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("docs/name-clearance.md", text, relative)

        incident = (REPO_ROOT /
                    "examples/name-clearance-incident-2026-08.md").read_text(
                        encoding="utf-8"
                    )
        for truth in (
                "plumbline-ai",
                "askalf/plumbline",
                "dbreunig/plumb",
                "does not prove legal clearance",
                "Writwall",
                "Grantcord",
                "Writcord"):
            self.assertIn(truth, incident)

        triage = (REPO_ROOT / "docs" / "agents" /
                  "triage-labels.md").read_text(encoding="utf-8")
        for label in ("bug", "enhancement", "needs-triage", "needs-info",
                      "ready-for-agent", "ready-for-human", "wontfix"):
            self.assertIn(f"`{label}`", triage)

        contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertIn("Public issue and pull-request workflow", contributing)
        self.assertIn("private governed source", contributing)
        self.assertIn("clean projection", contributing)


class RatifiedReleaseTests(DistributionTestCase):
    """Every ratification marker, and the package name, must agree."""

    def test_all_markers_agree(self):
        doctrine = (self.repo / "DOCTRINE.md").read_text(encoding="utf-8")
        self.assertIn("| Status | Ratified |", doctrine)
        row = next(l for l in doctrine.splitlines() if l.startswith("| 0.8 |"))
        self.assertTrue(row.rstrip().endswith("| Yes |"), row)
        self.assertIn("*Revision 0.8. Ratified 2026-08-21 by DR-005.", doctrine)

        record = (self.repo / "decisions" / "DR-005.md").read_text(encoding="utf-8")
        self.assertIn("HLLMR", record)
        self.assertIn("2026-08-21", record)
        self.assertNotIn("DRAFT — NO AUTHORITY", record)

        for name in ("README.md", "ADOPTING.md"):
            text = (self.repo / name).read_text(encoding="utf-8").lower()
            self.assertNotIn("ratification candidate", text, name)

    def test_builder_produces_the_final_release_name(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        archives = sorted((self.repo / "dist").glob("*.zip"))
        self.assertEqual([a.name for a in archives], ["writwall-0.8.zip"])

    def test_final_archive_passes_the_archive_check(self):
        self.build()
        result = self.check("--archive", "dist/writwall-0.8.zip")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_candidate_name_is_refused_once_ratified(self):
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(out / "writwall-0.6-rc.zip", "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
        self.assert_fails(self.check("--archive", "dist/writwall-0.6-rc.zip"), "archive")

    def test_candidate_state_still_produces_rc(self):
        self.make_candidate()
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        archives = sorted((self.repo / "dist").glob("*.zip"))
        self.assertEqual([a.name for a in archives], ["writwall-0.8-rc.zip"])


def adopt_fixture(repo):
    """Turn a pre-adoption fixture into a coherent post-adoption one.

    Deletes the adoption-record draft, issues every governance document still
    marked PROPOSED, and drops the '-PROPOSED' suffix from those filenames.
    Both steps are what the Owner actually performs at issue. A work order
    whose name still reads PROPOSED inside an adopted archive misstates its own
    status, which is the same defect the adoption-record rename exists to fix.

    A document left marked PROPOSED must fail the build instead of shipping;
    test_lingering_proposed_work_order_fails_the_build asserts that directly.
    """
    draft = repo / "governance" / "decisions" / "DR-001-ADOPTION-PROPOSED.md"
    if draft.is_file():
        draft.unlink()
    for path in sorted((repo / "governance").rglob("*.md")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        issued = text.replace("Status: PROPOSED", "Status: ISSUED")
        issued = issued.replace("status: PROPOSED", "status: ISSUED")
        if issued != text:
            path.write_text(issued, encoding="utf-8", newline="\n")
        if "-PROPOSED" in path.name:
            path.rename(path.with_name(path.name.replace("-PROPOSED", "")))
    (repo / "governance" / "decisions" / "DR-001.md").write_text(
        "# DR-001: Adoption of the Doctrine\n\n"
        "**Status: RATIFIED by the Owner, 2026-08-16.**\n\n"
        "D.2 Baseline commit: a905c879.\n", encoding="utf-8", newline="\n")


class GovernancePackagingGateTests(DistributionTestCase):
    """Owner disposition 2026-08-16: the finalized governance instance ships;
    unratified drafts never do; a contradictory state fails the build."""

    RECORD = "governance/decisions/DR-001.md"
    DRAFT = "governance/decisions/DR-001-ADOPTION-PROPOSED.md"

    def gov_entries(self, archive):
        with zipfile.ZipFile(archive) as handle:
            return [n for n in handle.namelist()
                    if n.startswith("writwall/governance/")]

    def build_ok(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return next((self.repo / "dist").glob("*.zip"))

    def sign_adoption_record(self):
        """Simulate the post-adoption state: signed record, no lingering drafts.

        The proposed work orders are *issued* rather than deleted, because that
        is what actually happens: the Owner issues WO-000 and WO-PL-006 and
        their status stops being PROPOSED. A governance document left marked
        PROPOSED at adoption must fail the build rather than ship, which
        test_lingering_proposed_work_order_fails_the_build asserts directly.
        """
        adopt_fixture(self.repo)

    # --- pre-adoption -----------------------------------------------------

    def test_pre_adoption_excludes_the_whole_governance_subtree(self):
        self.assertTrue((self.repo / self.DRAFT).is_file(), "fixture is pre-adoption")
        archive = self.build_ok()
        self.assertEqual(self.gov_entries(archive), [])

    def test_pre_adoption_archive_with_governance_fails_the_check(self):
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(out / "writwall-0.6.zip", "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
            archive.writestr("writwall/governance/PLAN.md", "x")
        self.assert_fails(self.check("--archive", "dist/writwall-0.6.zip"), "archive")

    def test_proposed_adoption_record_never_packaged(self):
        archive = self.build_ok()
        with zipfile.ZipFile(archive) as handle:
            names = handle.namelist()
        self.assertFalse(any("DR-001-ADOPTION-PROPOSED" in n for n in names), names)

    def test_archive_containing_the_proposed_record_fails(self):
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(out / "writwall-0.6.zip", "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
            archive.writestr(
                "writwall/governance/decisions/DR-001-ADOPTION-PROPOSED.md", "x")
        self.assert_fails(self.check("--archive", "dist/writwall-0.6.zip"), "archive")

    # --- adopted ----------------------------------------------------------

    def test_adopted_includes_the_finalized_instance(self):
        self.sign_adoption_record()
        archive = self.build_ok()
        entries = self.gov_entries(archive)
        self.assertIn("writwall/governance/decisions/DR-001.md", entries)
        self.assertIn("writwall/governance/PLAN.md", entries)
        self.assertFalse(any("PROPOSED" in n for n in entries), entries)

    def test_adopted_archive_passes_the_archive_check(self):
        self.sign_adoption_record()
        archive = self.build_ok()
        result = self.check("--archive", f"dist/{archive.name}")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_adopted_archive_without_the_record_fails(self):
        self.sign_adoption_record()
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(out / "writwall-0.6.zip", "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
        self.assert_fails(self.check("--archive", "dist/writwall-0.6.zip"), "archive")

    def test_a_marker_inside_the_scan_window_is_detected(self):
        """A governance document declaring PROPOSED inside the scan window is
        detected, and an adopted-state build refuses it by name.

        The gate reads only a fixed window at the top of each document, so a
        draft's status line has to fall inside it. This asserts that from a
        synthetic document placed near the far edge of the window: no live
        work-order filename and no live lifecycle stage participates, so the
        Owner issuing, renaming, or removing a real draft cannot make this
        test stale. Frontmatter alone is deliberately absent here, because the
        explicit marker is what the scan matches and therefore what every
        governed draft must carry.
        """
        self.sign_adoption_record()
        draft = self.repo / "governance" / "work-orders" / "WO-997-WINDOW.md"
        padding = "\n".join(f"filler line {n}" for n in range(1, 36))
        draft.write_text(f"# Draft\n\n{padding}\n\nStatus: PROPOSED — draft\n",
                         encoding="utf-8", newline="\n")

        lines = draft.read_text(encoding="utf-8").splitlines()
        marker_index = next(i for i, line in enumerate(lines)
                            if "Status: PROPOSED" in line)
        self.assertLess(marker_index, 40,
                        "fixture must place the marker inside the scan window")

        result = self.build()
        self.assertNotEqual(result.returncode, 0,
                            "the build shipped a document marked PROPOSED")
        self.assertIn("WO-997-WINDOW.md", result.stderr + result.stdout)

    def test_lingering_proposed_work_order_fails_the_build(self):
        """A signed record plus any still-PROPOSED governance document is a
        partially adopted state, and the build must refuse rather than ship."""
        self.sign_adoption_record()
        lingering = self.repo / "governance" / "work-orders" / "WO-999-LINGERING.md"
        lingering.write_text(
            "---\nstatus: PROPOSED\n# Status: PROPOSED — draft\n---\n\n# Draft\n",
            encoding="utf-8", newline="\n")
        result = self.build()
        self.assertNotEqual(result.returncode, 0,
                            "the build shipped a partially adopted state")
        self.assertIn("PROPOSED", result.stderr + result.stdout)

    # --- contradictory: the build must FAIL, not ship ---------------------

    def test_signed_record_and_draft_together_fail_the_build(self):
        (self.repo / self.RECORD).write_text(
            "# DR-001\n\n**Status: RATIFIED by the Owner, 2026-08-16.**\n",
            encoding="utf-8", newline="\n")
        result = self.build()
        self.assertNotEqual(result.returncode, 0,
                            "build shipped a contradictory governance state")
        self.assertIn("contradictory", (result.stderr + result.stdout).lower())

    def test_signed_record_still_marked_proposed_fails_the_build(self):
        (self.repo / self.DRAFT).unlink()
        (self.repo / self.RECORD).write_text(
            "# DR-001\n\n**Status: PROPOSED.**\n", encoding="utf-8", newline="\n")
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("proposed", (result.stderr + result.stdout).lower())

    def test_signed_record_with_proposed_plan_fails_the_build(self):
        self.sign_adoption_record()
        plan = self.repo / "governance" / "PLAN.md"
        plan.write_text("# PLAN\n\n**Status: PROPOSED.**\n", encoding="utf-8", newline="\n")
        result = self.build()
        self.assertNotEqual(result.returncode, 0,
                            "build shipped a partially adopted state")
        self.assertIn("partially adopted", (result.stderr + result.stdout).lower())

    def test_signed_record_with_proposed_routing_fails_the_build(self):
        self.sign_adoption_record()
        routing = self.repo / "governance" / "ROUTING.md"
        routing.write_text("# ROUTING\n\n**Status: PROPOSED.**\n", encoding="utf-8", newline="\n")
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("partially adopted", (result.stderr + result.stdout).lower())

    def test_checker_reports_contradictory_state(self):
        (self.repo / self.RECORD).write_text(
            "# DR-001\n\n**Status: RATIFIED by the Owner, 2026-08-16.**\n",
            encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "governance-state")

    # --- no adoption route ever receives the instance ---------------------

    def test_governance_never_enters_the_adoption_bundle(self):
        target = (self.repo / "skills" / "writwall-adopt" / "assets"
                  / "governance")
        target.mkdir(parents=True)
        (target / "PLAN.md").write_text("x", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "segregation")


class MachineSpecificDataTests(DistributionTestCase):
    """Charter kill list: no release archive carries local absolute paths or
    machine-specific data."""

    def test_enforcement_installation_is_not_packaged(self):
        claude = self.repo / ".claude" / "hooks"
        claude.mkdir(parents=True, exist_ok=True)
        (claude / "wo_capability_wall.py").write_text("x", encoding="utf-8", newline="\n")
        (self.repo / ".claude" / "settings.json").write_text(
            '{"hooks": {}}', encoding="utf-8", newline="\n")
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        archive = next((self.repo / "dist").glob("*.zip"))
        with zipfile.ZipFile(archive) as handle:
            self.assertFalse([n for n in handle.namelist() if "/.claude/" in n])

    def test_archive_carrying_the_enforcement_installation_fails(self):
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(out / "writwall-0.6.zip", "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
            archive.writestr("writwall/.claude/settings.json", '{"hooks": {}}')
        self.assert_fails(self.check("--archive", "dist/writwall-0.6.zip"), "archive")

    def test_build_machine_path_in_a_shipped_file_fails(self):
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(out / "writwall-0.6.zip", "w") as archive:
            # The path of the repository that built this archive, which is the
            # fixture copy, not the real repository.
            archive.writestr("writwall/README.md",
                             f"install from {self.repo.as_posix()}/adapters\n")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
        self.assert_fails(self.check("--archive", "dist/writwall-0.6.zip"), "archive")

    def test_real_archive_is_free_of_machine_paths(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        archive = next((self.repo / "dist").glob("*.zip"))
        builder = load_distribution_builder()
        needles = {str(REPO_ROOT), REPO_ROOT.as_posix(),
                   str(Path.home()), Path.home().as_posix()}
        with zipfile.ZipFile(archive) as handle:
            for name in handle.namelist():
                if name.endswith("/"):
                    continue
                if not name.lower().endswith((".md", ".py", ".sh", ".json", ".txt")):
                    continue
                text = handle.read(name).decode("utf-8", errors="ignore").lower()
                for needle in needles:
                    self.assertFalse(
                        builder.machine_path_occurs(text, needle),
                        f"{name} leaks {needle}")

    def test_historical_archive_is_scanned_and_carries_no_machine_path(self):
        """RFI-15: `archive/**` ships, so it is scanned like every other shipped
        subtree.

        The former blanket exemption predates RFI-09, which made
        `archive/pre-adoption-bootstrap/` a deliberate shipping target. Old
        absolute paths that belong to some *other* machine remain historical
        evidence and are still allowed; this build machine's own root and home
        are not.
        """
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        archive = next((self.repo / "dist").glob("*.zip"))
        result = self.check("--archive", f"dist/{archive.name}")
        self.assertEqual(result.returncode, 0, result.stdout)


class HookRegistrationTests(DistributionTestCase):
    """The project hook registration must be portable and match canon."""

    SETTINGS = ".claude/settings.json"
    INSTALLED = ".claude/hooks/wo_capability_wall.py"

    def write_settings(self, command, *, timeout=10):
        path = self.repo / self.SETTINGS
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "*", "hooks": [{"type": "command", "command": command,
                                           "timeout": timeout}]}]}},
            indent=2) + "\n", encoding="utf-8", newline="\n")

    def test_real_registration_is_portable(self):
        data = json.loads((self.repo / self.SETTINGS).read_text(encoding="utf-8"))
        command = data["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        self.assertEqual(
            command,
            'py -3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/wo_capability_wall.py"')
        self.assertEqual(data["hooks"]["PreToolUse"][0]["matcher"], "*")
        self.assertEqual(data["hooks"]["PreToolUse"][0]["hooks"][0]["timeout"], 10)
        self.assertEqual(self.check().returncode, 0)

    def test_registration_without_explicit_timeout_fails(self):
        path = self.repo / self.SETTINGS
        data = json.loads(path.read_text(encoding="utf-8"))
        del data["hooks"]["PreToolUse"][0]["hooks"][0]["timeout"]
        path.write_text(json.dumps(data), encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "hook-registration")

    def test_absolute_repository_path_in_registration_fails(self):
        self.write_settings(
            f'python "{self.repo.as_posix()}/.claude/hooks/wo_capability_wall.py"')
        self.assert_fails(self.check(), "hook-registration")

    def test_absolute_drive_path_in_registration_fails(self):
        self.write_settings('python "C:/tools/.claude/hooks/wo_capability_wall.py"')
        self.assert_fails(self.check(), "hook-registration")

    def test_absolute_posix_path_in_registration_fails(self):
        self.write_settings('python "/home/someone/.claude/hooks/wo_capability_wall.py"')
        self.assert_fails(self.check(), "hook-registration")

    def test_registration_lacking_project_dir_variable_fails(self):
        self.write_settings('python ".claude/hooks/wo_capability_wall.py"')
        self.assert_fails(self.check(), "hook-registration")

    def test_wrong_matcher_fails(self):
        path = self.repo / self.SETTINGS
        path.write_text(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Edit|Write", "hooks": [{"type": "command",
             "command": 'python "${CLAUDE_PROJECT_DIR}/.claude/hooks/wo_capability_wall.py"'}]}]}}),
            encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "hook-registration")

    def test_installed_adapter_differing_from_canonical_fails(self):
        installed = self.repo / self.INSTALLED
        installed.parent.mkdir(parents=True, exist_ok=True)
        installed.write_text("# locally modified wall\n", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "hook-registration")

    def test_installed_adapter_matches_canonical(self):
        self.assertEqual(
            (self.repo / self.INSTALLED).read_bytes(),
            (self.repo / "adapters" / "claude-code" / "wo_capability_wall.py").read_bytes())

    def test_malformed_settings_json_fails(self):
        (self.repo / self.SETTINGS).write_text("{not json", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "hook-registration")


class ClaudeDirPackagingTests(DistributionTestCase):
    """Pre-adoption: excluded. Post-adoption: exactly two files."""

    RECORD = "governance/decisions/DR-001.md"
    DRAFT = "governance/decisions/DR-001-ADOPTION-PROPOSED.md"

    def sign(self):
        adopt_fixture(self.repo)

    def build_ok(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return next((self.repo / "dist").glob("*.zip"))

    def claude_entries(self, archive):
        with zipfile.ZipFile(archive) as handle:
            return sorted(n[len("writwall/"):] for n in handle.namelist()
                          if n.startswith("writwall/.claude/"))

    def test_pre_adoption_excludes_the_installation(self):
        self.assertEqual(self.claude_entries(self.build_ok()), [])

    def test_post_adoption_includes_exactly_two_files(self):
        self.sign()
        self.assertEqual(
            self.claude_entries(self.build_ok()),
            [".claude/hooks/wo_capability_wall.py", ".claude/settings.json"])

    def test_post_adoption_archive_passes_the_check(self):
        self.sign()
        archive = self.build_ok()
        self.assertEqual(self.check("--archive", f"dist/{archive.name}").returncode, 0)

    def test_machine_local_files_are_never_packaged(self):
        self.sign()
        claude = self.repo / ".claude"
        (claude / "settings.local.json").write_text('{"x": 1}', encoding="utf-8", newline="\n")
        (claude / "cache.tmp").write_text("junk", encoding="utf-8", newline="\n")
        entries = self.claude_entries(self.build_ok())
        self.assertNotIn(".claude/settings.local.json", entries)
        self.assertNotIn(".claude/cache.tmp", entries)

    def test_archive_carrying_active_wo_pointer_fails(self):
        self.sign()
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(out / "writwall-0.6.zip", "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
            archive.writestr("writwall/.claude/settings.json", "{}")
            archive.writestr("writwall/.claude/hooks/wo_capability_wall.py", "x")
            archive.writestr("writwall/.claude/active-wo.txt", "x")
            archive.writestr("writwall/governance/decisions/DR-001.md", "x")
        self.assert_fails(self.check("--archive", "dist/writwall-0.6.zip"), "archive")

    def test_archive_carrying_settings_local_fails(self):
        self.sign()
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(out / "writwall-0.6.zip", "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
            archive.writestr("writwall/.claude/settings.json", "{}")
            archive.writestr("writwall/.claude/hooks/wo_capability_wall.py", "x")
            archive.writestr("writwall/.claude/settings.local.json", "{}")
            archive.writestr("writwall/governance/decisions/DR-001.md", "x")
        self.assert_fails(self.check("--archive", "dist/writwall-0.6.zip"), "archive")

    def test_pre_adoption_archive_with_installation_fails(self):
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(out / "writwall-0.6.zip", "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
            archive.writestr("writwall/.claude/settings.json", "{}")
        self.assert_fails(self.check("--archive", "dist/writwall-0.6.zip"), "archive")

    def test_adoption_routes_never_receive_writwalls_installation(self):
        target = self.repo / "skills" / "writwall-adopt" / "assets" / ".claude"
        target.mkdir(parents=True)
        (target / "settings.json").write_text("{}", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "segregation")


class LineEndingPreflightTests(DistributionTestCase):
    """Deterministic CRLF preflight. Never normalizes; fails with paths."""

    def to_crlf(self, relative):
        path = self.repo / relative
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))

    def test_crlf_canonical_source_fails_the_build(self):
        self.to_crlf("DOCTRINE.md")
        result = self.build()
        self.assertNotEqual(result.returncode, 0, "build produced a hash over CRLF bytes")
        output = result.stderr + result.stdout
        self.assertIn("CRLF", output)
        self.assertIn("DOCTRINE.md", output)

    def test_crlf_bundled_copy_fails_the_build(self):
        self.to_crlf("skills/writwall-adopt/references/DOCTRINE.md")
        result = self.build()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("skills/writwall-adopt/references/DOCTRINE.md",
                      result.stderr + result.stdout)

    def test_build_does_not_silently_normalize(self):
        self.to_crlf("README.md")
        self.build()
        self.assertIn(b"\r\n", (self.repo / "README.md").read_bytes(),
                      "the builder normalized the working tree instead of failing")

    def test_crlf_reported_by_the_checker_too(self):
        self.to_crlf("README.md")
        self.assert_fails(self.check(), "line-endings")

    def test_lf_files_pass(self):
        self.assertEqual(self.check().returncode, 0)
        self.assertEqual(self.build().returncode, 0)

    def test_archive_bytes_match_the_validated_working_tree(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)
        archive = next((self.repo / "dist").glob("*.zip"))
        with zipfile.ZipFile(archive) as handle:
            for name in handle.namelist():
                if name.endswith("/") or name == "writwall/MANIFEST.sha256":
                    continue
                on_disk = self.repo / name[len("writwall/"):]
                self.assertTrue(on_disk.is_file(), name)
                self.assertEqual(handle.read(name), on_disk.read_bytes(),
                                 f"{name} differs from the working-tree bytes")


class BuilderTests(DistributionTestCase):
    def build_and_open(self):
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        archives = sorted((self.repo / "dist").glob("*.zip"))
        self.assertEqual(len(archives), 1, archives)
        return archives[0]

    def test_candidate_name_while_unratified(self):
        self.make_candidate()
        archive = self.build_and_open()
        self.assertEqual(archive.name, "writwall-0.8-rc.zip")

    def test_single_top_level_directory(self):
        archive = self.build_and_open()
        with zipfile.ZipFile(archive) as handle:
            roots = {name.split("/", 1)[0] for name in handle.namelist()}
        self.assertEqual(roots, {"writwall"})

    def test_excludes_build_and_bootstrap_and_report(self):
        (self.repo / "bootstrap").mkdir(exist_ok=True)
        (self.repo / "bootstrap" / "WO.md").write_text("x", encoding="utf-8", newline="\n")
        (self.repo / "REMEDIATION-REPORT.md").write_text("x", encoding="utf-8", newline="\n")
        archive = self.build_and_open()
        with zipfile.ZipFile(archive) as handle:
            names = handle.namelist()
        for name in names:
            self.assertNotIn("/bootstrap/", name)
            self.assertNotIn("/dist/", name)
            self.assertNotIn("__pycache__", name)
            self.assertFalse(name.endswith("REMEDIATION-REPORT.md"), name)

    def test_excludes_every_per_work_order_report(self):
        """Reports are named REMEDIATION-REPORT-WO-PL-00n.md. An exact-name
        exclusion ships every one after the first."""
        for suffix in ("", "-WO-PL-001", "-WO-PL-002", "-WO-PL-999"):
            (self.repo / f"REMEDIATION-REPORT{suffix}.md").write_text("x", encoding="utf-8", newline="\n")
        (self.repo / "REMEDIATION-INVENTORY.md").write_text("x", encoding="utf-8", newline="\n")
        archive = self.build_and_open()
        with zipfile.ZipFile(archive) as handle:
            leaked = [n for n in handle.namelist() if "REMEDIATION" in n]
        self.assertEqual(leaked, [], f"reports leaked into the distribution: {leaked}")

    def test_archive_containing_a_per_work_order_report_fails_the_check(self):
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(out / "writwall-0.6.zip", "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
            archive.writestr("writwall/REMEDIATION-REPORT-WO-PL-002.md", "x")
        self.assert_fails(self.check("--archive", "dist/writwall-0.6.zip"), "archive")

    def test_manifest_present_and_correct(self):
        archive = self.build_and_open()
        import hashlib
        with zipfile.ZipFile(archive) as handle:
            manifest = handle.read("writwall/MANIFEST.sha256").decode("utf-8")
            entries = {}
            for line in manifest.splitlines():
                digest, _, relative = line.partition("  ")
                entries[relative] = digest
            self.assertGreater(len(entries), 20)
            for relative, digest in entries.items():
                data = handle.read(f"writwall/{relative}")
                self.assertEqual(hashlib.sha256(data).hexdigest(), digest, relative)

    def test_no_nested_zip_in_archive(self):
        archive = self.build_and_open()
        with zipfile.ZipFile(archive) as handle:
            for name in handle.namelist():
                self.assertFalse(name.lower().endswith(".zip"), name)

    def test_built_archive_passes_the_archive_check(self):
        archive = self.build_and_open()
        result = self.check("--archive", f"dist/{archive.name}")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_final_release_name_only_when_both_markers_ratified(self):
        self.make_candidate()
        self.set_dc1_status("Ratified")
        self.set_dc2_ratified("Yes")
        archive = self.build_and_open()
        self.assertEqual(archive.name, "writwall-0.8.zip")

    def test_candidate_name_when_only_dc2_flipped(self):
        # DC.2 says ratified, DC.1 still a candidate: not a release.
        self.set_dc1_status("Ratification candidate")
        archive = self.build_and_open()
        self.assertEqual(archive.name, "writwall-0.8-rc.zip")

    def test_candidate_name_when_only_dc1_flipped(self):
        # DC.1 says ratified, DC.2 still pending: not a release.
        self.set_dc2_ratified("Pending")
        archive = self.build_and_open()
        self.assertEqual(archive.name, "writwall-0.8-rc.zip")


class ArchiveCheckFailureTests(DistributionTestCase):
    def make_archive(self, names, filename="writwall-0.6-rc.zip"):
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        path = out / filename
        with zipfile.ZipFile(path, "w") as archive:
            for name in names:
                archive.writestr(name, "x")
        return path

    def test_two_top_level_directories_fail(self):
        self.make_archive(["writwall/README.md", "other/README.md",
                           "writwall/MANIFEST.sha256"])
        self.assert_fails(self.check("--archive", "dist/writwall-0.6-rc.zip"), "archive")

    def test_forbidden_path_inside_archive_fails(self):
        self.make_archive(["writwall/README.md", "writwall/MANIFEST.sha256",
                           "writwall/mnt/user-data/x.md"])
        self.assert_fails(self.check("--archive", "dist/writwall-0.6-rc.zip"), "archive")

    def test_nested_zip_inside_archive_fails(self):
        self.make_archive(["writwall/README.md", "writwall/MANIFEST.sha256",
                           "writwall/inner.zip"])
        self.assert_fails(self.check("--archive", "dist/writwall-0.6-rc.zip"), "archive")

    def test_missing_manifest_fails(self):
        self.make_archive(["writwall/README.md"])
        self.assert_fails(self.check("--archive", "dist/writwall-0.6-rc.zip"), "archive")

    def test_final_release_name_while_candidate_fails(self):
        self.make_archive(["writwall/README.md", "writwall/MANIFEST.sha256"],
                          filename="writwall-0.6.zip")
        self.assert_fails(self.check("--archive", "dist/writwall-0.6.zip"), "archive")

    def test_bootstrap_leaking_into_archive_fails(self):
        self.make_archive(["writwall/README.md", "writwall/MANIFEST.sha256",
                           "writwall/bootstrap/WO.md"])
        self.assert_fails(self.check("--archive", "dist/writwall-0.6-rc.zip"), "archive")

    def test_missing_archive_fails(self):
        self.assert_fails(self.check("--archive", "dist/nope.zip"), "archive")


# --------------------------------------------------------------------------
# Deterministic archive (WO-PL-005-R1, RFI-11)
# --------------------------------------------------------------------------

# Mirrors of the builder's declared policy. Duplicated deliberately: a test
# that imported the builder's own constants would pass no matter what they
# were changed to, which is not evidence.
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ZIP_CREATE_SYSTEM = 3          # Unix, so external_attr carries the mode
MODE_EXECUTABLE = 0o755
MODE_REGULAR = 0o644
EXECUTABLE_ARCNAMES = {"writwall/init.sh"}


class DeterministicArchiveTests(DistributionTestCase):
    """The archive's bytes must be a function of file CONTENT and PATH only.

    Nothing about the build host may leak in: not source mtimes, not umask,
    not the platform's creator-system code, not the moment of the build.

    Comparing extracted contents is not enough. The whole ZIP byte stream is
    the artifact whose SHA-256 gets published, so that is what these tests
    compare.
    """

    def build_in(self, repo):
        result = subprocess.run(
            [sys.executable, str(repo / "scripts" / "build_distribution.py"),
             "--output", "dist/"], capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return next((repo / "dist").glob("*.zip"))

    def rebuild(self, repo=None):
        repo = repo or self.repo
        for stale in (repo / "dist").glob("*.zip"):
            stale.unlink()
        return self.build_in(repo)

    @staticmethod
    def digest(path):
        import hashlib
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def set_all_mtimes(repo, when):
        import os
        for path in sorted(repo.rglob("*")):
            if path.is_file() and "dist" not in path.parts:
                os.utime(path, (when, when))

    # -- the headline claim -------------------------------------------------

    def test_two_builds_of_an_unchanged_tree_are_byte_identical(self):
        first = self.digest(self.build_in(self.repo))
        second = self.digest(self.rebuild())
        self.assertEqual(first, second,
                         "two builds of an unchanged tree produced different "
                         "archive bytes; the published hash is meaningless")

    def test_identical_trees_with_different_mtimes_build_identical_archives(self):
        """The strong form: a fresh checkout has different mtimes than the tree
        the release was built from, and must still reproduce the hash."""
        other = copy_repo(self.tmp / "writwall-b")
        # Deliberately far apart, and neither is "now".
        self.set_all_mtimes(self.repo, 1_000_000_000)   # 2001-09-09
        self.set_all_mtimes(other, 1_600_000_000)       # 2020-09-13

        a = self.build_in(self.repo)
        b = self.build_in(other)

        self.assertEqual(a.read_bytes(), b.read_bytes(),
                         "source mtimes leaked into the archive bytes")
        self.assertEqual(self.digest(a), self.digest(b))

    # -- entry metadata -----------------------------------------------------

    def test_every_entry_carries_the_fixed_metadata(self):
        archive = self.build_in(self.repo)
        with zipfile.ZipFile(archive) as handle:
            infos = handle.infolist()
        self.assertTrue(infos)
        manifest_seen = False
        for info in infos:
            with self.subTest(entry=info.filename):
                self.assertEqual(info.date_time, ZIP_TIMESTAMP)
                self.assertEqual(info.create_system, ZIP_CREATE_SYSTEM)
                self.assertEqual(info.extra, b"")
                self.assertEqual(info.comment, b"")
                self.assertEqual(info.internal_attr, 0)
                self.assertEqual(info.flag_bits & 0x08, 0)
            if info.filename == "writwall/MANIFEST.sha256":
                manifest_seen = True
        self.assertTrue(manifest_seen,
                        "MANIFEST.sha256 must be normalized like every other entry")

    def test_archive_comment_is_empty(self):
        with zipfile.ZipFile(self.build_in(self.repo)) as handle:
            self.assertEqual(handle.comment, b"")

    def test_permissions_follow_the_declared_policy(self):
        archive = self.build_in(self.repo)
        with zipfile.ZipFile(archive) as handle:
            infos = handle.infolist()
        for info in infos:
            mode = (info.external_attr >> 16) & 0o777
            expected = (MODE_EXECUTABLE if info.filename in EXECUTABLE_ARCNAMES
                        else MODE_REGULAR)
            with self.subTest(entry=info.filename):
                self.assertEqual(mode, expected, f"{info.filename} mode {mode:o}")

    def test_init_sh_is_executable_and_documents_are_not(self):
        archive = self.build_in(self.repo)
        with zipfile.ZipFile(archive) as handle:
            modes = {i.filename: (i.external_attr >> 16) & 0o777
                     for i in handle.infolist()}
        self.assertEqual(modes["writwall/init.sh"], MODE_EXECUTABLE)
        for name, mode in modes.items():
            if name == "writwall/init.sh":
                continue
            with self.subTest(entry=name):
                self.assertEqual(mode, MODE_REGULAR)
                self.assertFalse(mode & 0o111, f"{name} is marked executable")

    def test_entry_order_is_sorted_and_stable(self):
        with zipfile.ZipFile(self.build_in(self.repo)) as handle:
            first = handle.namelist()
        with zipfile.ZipFile(self.rebuild()) as handle:
            second = handle.namelist()
        self.assertEqual(first, sorted(first), "entry order is not sorted")
        self.assertEqual(first, second, "entry order is not stable across builds")

    # -- contents and manifest are unaffected -------------------------------

    def test_manifest_verifies_against_the_exact_stored_bytes(self):
        """Normalizing metadata must not disturb content or the manifest."""
        import hashlib
        archive = self.build_in(self.repo)
        with zipfile.ZipFile(archive) as handle:
            manifest = handle.read("writwall/MANIFEST.sha256").decode("utf-8")
            recorded = {path: digest for digest, _, path in
                        (line.partition("  ") for line in manifest.splitlines())}
            self.assertTrue(recorded)
            for name in handle.namelist():
                if name == "writwall/MANIFEST.sha256":
                    continue
                rel = name[len("writwall/"):]
                self.assertIn(rel, recorded, f"{rel} missing from the manifest")
                stored = handle.read(name)
                self.assertEqual(hashlib.sha256(stored).hexdigest(), recorded[rel],
                                 f"manifest hash does not match stored bytes for {rel}")
            self.assertEqual(len(recorded), len(handle.namelist()) - 1)

    def test_stored_bytes_still_equal_the_source_files(self):
        archive = self.build_in(self.repo)
        with zipfile.ZipFile(archive) as handle:
            for name in handle.namelist():
                if name == "writwall/MANIFEST.sha256":
                    continue
                source = self.repo / name[len("writwall/"):]
                with self.subTest(entry=name):
                    self.assertTrue(source.is_file(), name)
                    self.assertEqual(handle.read(name), source.read_bytes())


class ProposedStatusDetectionTests(DistributionTestCase):
    """RFI-14: proposed-status detection must be semantic, not one literal.

    The pre-fix gate matched the single literal `Status: PROPOSED` inside a
    fixed 40-line window. A draft carrying ordinary lowercase frontmatter, a
    quoted value, a different capitalization, or a long frontmatter block
    walked straight through the adopted-state gate and would have shipped.

    Every fixture here is synthetic and lives in packageable history so the
    proposed-status classifier is exercised independently of the transient
    live-work gate. No live lifecycle stage participates, so the Owner issuing,
    renaming, or removing a real draft cannot make these tests stale (the
    RFI-12 rule).
    """

    def plant(self, name, text, subdir="history"):
        path = self.repo / "governance" / subdir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def assert_blocks(self, name, text, subdir="history"):
        """The builder refuses by name, and the checker independently agrees."""
        adopt_fixture(self.repo)
        self.plant(name, text, subdir)
        built = self.build()
        output = built.stdout + built.stderr
        self.assertNotEqual(built.returncode, 0,
                            f"the build shipped a document marked PROPOSED:\n{output}")
        self.assertIn(name, output)
        checked = self.check()
        self.assertNotEqual(checked.returncode, 0,
                            f"builder and checker disagree:\n{checked.stdout}")
        self.assertIn("governance-state", checked.stdout)

    def assert_allows(self, name, text, subdir="history"):
        """Neither the builder nor the checker treats the document as PROPOSED."""
        adopt_fixture(self.repo)
        self.plant(name, text, subdir)
        built = self.build()
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        checked = self.check()
        self.assertEqual(checked.returncode, 0, checked.stdout)

    # --- must block -------------------------------------------------------

    def test_lowercase_frontmatter_only_proposed_blocks(self):
        """RFI-14 exactly: no explicit marker, only ordinary frontmatter."""
        self.assert_blocks(
            "WO-990-LOWERCASE.md",
            "---\nid: WO-990\nstatus: proposed\n---\n\n# Draft\n\nBody text.\n")

    def test_mixed_case_proposed_blocks(self):
        self.assert_blocks(
            "WO-991-MIXEDCASE.md",
            "---\nid: WO-991\nStatus: Proposed\n---\n\n# Draft\n")

    def test_quoted_proposed_value_blocks(self):
        self.assert_blocks(
            "WO-992-QUOTED.md",
            '---\nid: WO-992\nstatus:   "PROPOSED"   \n---\n\n# Draft\n')

    def test_single_quoted_and_padded_proposed_value_blocks(self):
        self.assert_blocks(
            "WO-994-PADDED.md",
            "---\nid: WO-994\n status_note: unrelated\nstatus: 'proposed'\n---\n\n# Draft\n")

    def test_proposed_field_beyond_the_scan_window_but_inside_frontmatter_blocks(self):
        filler = "\n".join(f"note_{n}: filler value {n}" for n in range(1, 46))
        text = f"---\nid: WO-993\n{filler}\nstatus: PROPOSED\n---\n\n# Draft\n"
        lines = text.splitlines()
        index = next(i for i, line in enumerate(lines) if line.startswith("status:"))
        self.assertGreater(index, 40,
                           "fixture must place the field beyond the marker window")
        self.assert_blocks("WO-993-BEYOND-WINDOW.md", text)

    def test_explicit_marker_without_frontmatter_still_blocks(self):
        """The pre-existing human-readable convention must keep working."""
        self.assert_blocks(
            "WO-995-MARKER.md",
            "# Draft\n\n**Status: PROPOSED.** Not authority.\n")

    def test_heading_marker_without_frontmatter_still_blocks(self):
        self.assert_blocks(
            "WO-996-HEADING.md",
            "# Draft\n\n# Status: PROPOSED - not authority\n")

    # --- must not block ---------------------------------------------------

    def test_final_statuses_do_not_block(self):
        adopt_fixture(self.repo)
        for status in ("ISSUED", "ACTIVE", "COMPLETE", "RATIFIED", "RFI-BLOCKED"):
            with self.subTest(status=status):
                name = f"WO-980-{status.replace('-', '')}.md"
                path = self.plant(
                    name, f"---\nid: WO-980\nstatus: {status}\n---\n\n# Record\n")
                try:
                    built = self.build()
                    self.assertEqual(built.returncode, 0,
                                     built.stdout + built.stderr)
                    checked = self.check()
                    self.assertEqual(checked.returncode, 0, checked.stdout)
                finally:
                    path.unlink()

    def test_prose_mentions_do_not_block(self):
        """Ordinary prose discussing the words 'status' and 'proposed'."""
        self.assert_allows(
            "WO-981-PROSE.md",
            "# Notes\n\n"
            "This note discusses the status of a proposed amendment. The\n"
            "proposed status of that draft was PROPOSED at the time it was\n"
            "written; status changes are recorded in the log. A status of\n"
            "proposed carries no authority.\n")

    def test_a_completed_record_with_historical_proposed_language_does_not_block(self):
        """A record whose frontmatter declares a final status is final, even
        though its body quotes the language it carried while it was a draft."""
        self.assert_allows(
            "WO-982-COMPLETED.md",
            "---\nid: WO-982\nstatus: COMPLETE\n---\n\n"
            "# Completed record\n\n"
            "As drafted this document opened with `status: PROPOSED` and a\n"
            "**Status: PROPOSED.** marker line. Both were removed at issue.\n")

    def test_archived_bootstrap_record_outside_governance_does_not_block(self):
        """`archive/**` is closed-historical evidence, not live governance
        state, so a PROPOSED marker there cannot make the live state
        contradictory."""
        adopt_fixture(self.repo)
        target = (self.repo / "archive" / "pre-adoption-bootstrap"
                  / "WO-983-ARCHIVED.md")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "# Archived bootstrap work order\n\n"
            "**Status: PROPOSED.** Retained exactly as drafted; superseded.\n",
            encoding="utf-8", newline="\n")
        built = self.build()
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        checked = self.check()
        self.assertEqual(checked.returncode, 0, checked.stdout)

    # --- the two implementations must agree -------------------------------

    def test_builder_and_checker_agree_on_every_fixture(self):
        """A gate the builder enforces and the checker does not is theatre."""
        blocking = {
            "WO-970-A.md": "---\nstatus: proposed\n---\n\n# Draft\n",
            "WO-970-B.md": "---\nStatus: Proposed\n---\n\n# Draft\n",
            "WO-970-C.md": '---\nstatus: "PROPOSED"\n---\n\n# Draft\n',
            "WO-970-D.md": "# Draft\n\n**Status: PROPOSED.**\n",
        }
        allowing = {
            "WO-971-A.md": "---\nstatus: COMPLETE\n---\n\n# Record\n",
            "WO-971-B.md": "---\nstatus: ISSUED\n---\n\n# Record\n",
            "WO-971-C.md": "# Record\n\nThe proposed status was recorded here.\n",
        }
        adopt_fixture(self.repo)
        for name, text in blocking.items():
            with self.subTest(fixture=name, expected="block"):
                path = self.plant(name, text)
                try:
                    built = self.build()
                    checked = self.check()
                    self.assertNotEqual(built.returncode, 0,
                                        built.stdout + built.stderr)
                    self.assertNotEqual(checked.returncode, 0, checked.stdout)
                finally:
                    path.unlink()
        for name, text in allowing.items():
            with self.subTest(fixture=name, expected="allow"):
                path = self.plant(name, text)
                try:
                    built = self.build()
                    checked = self.check()
                    self.assertEqual(built.returncode, 0,
                                     built.stdout + built.stderr)
                    self.assertEqual(checked.returncode, 0, checked.stdout)
                finally:
                    path.unlink()


class ShippedArchiveMachinePathTests(DistributionTestCase):
    """RFI-15: no packageable subtree is exempt merely because it is historical.

    `archive/pre-adoption-bootstrap/` became a deliberate shipping target when
    the Owner disposed RFI-09. The blanket `writwall/archive/` exemption
    predates that disposition, so this build machine's own path shipped
    unchecked inside evidence the archive is meant to carry.
    """

    def minimal_archive(self, extra, filename="writwall-0.6.zip"):
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        target = out / filename
        with zipfile.ZipFile(target, "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
            for name, body in extra.items():
                archive.writestr(name, body)
        return target

    # --- the checker rejects a hand-built archive -------------------------

    def test_build_machine_path_inside_shipped_archive_evidence_fails(self):
        entry = "writwall/archive/pre-adoption-bootstrap/EVIDENCE.md"
        self.minimal_archive(
            {entry: f"| 1 | Project root | `{self.repo.as_posix()}` |\n"})
        result = self.check("--archive", "dist/writwall-0.6.zip")
        self.assert_fails(result, "archive")
        self.assertIn(entry, result.stdout)
        self.assertIn("build machine's own path", result.stdout)

    def test_build_machine_home_path_inside_shipped_archive_evidence_fails(self):
        entry = "writwall/archive/proposed-v0.1/HISTORY.md"
        home = Path.home().as_posix()
        self.minimal_archive(
            {entry: f"the operator profile used at the time was {home}/Documents\n"})
        result = self.check("--archive", "dist/writwall-0.6.zip")
        self.assert_fails(result, "archive")
        self.assertIn(entry, result.stdout)

    # --- the builder refuses before a candidate exists --------------------

    def test_builder_refuses_machine_path_in_shipped_archive_evidence(self):
        target = self.repo / "archive" / "pre-adoption-bootstrap" / "LEAK.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"project root: {self.repo.as_posix()}\n",
                          encoding="utf-8", newline="\n")
        result = self.build()
        output = (result.stdout + result.stderr).replace("\\", "/")
        self.assertNotEqual(result.returncode, 0,
                            f"the builder produced a candidate carrying a "
                            f"machine path:\n{output}")
        self.assertIn("archive/pre-adoption-bootstrap/LEAK.md", output)
        self.assertFalse(list((self.repo / "dist").glob("*.zip")),
                         "a candidate archive was created despite the refusal")

    def test_no_packageable_subtree_is_blanket_exempt(self):
        for relative in ("archive/pre-adoption-bootstrap/LEAK.md",
                         "archive/proposed-v0.1/LEAK.md",
                         "archive/LEAK.md",
                         "templates/LEAK.md",
                         "examples/LEAK.md"):
            with self.subTest(path=relative):
                target = self.repo / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(f"root: {self.repo.as_posix()}\n",
                                  encoding="utf-8", newline="\n")
                try:
                    result = self.build()
                    output = (result.stdout + result.stderr).replace("\\", "/")
                    self.assertNotEqual(result.returncode, 0,
                                        f"{relative} was exempt:\n{output}")
                    self.assertIn(relative, output)
                finally:
                    target.unlink()

    # --- what must still be allowed ---------------------------------------

    def test_generic_example_paths_in_shipped_archive_remain_allowed(self):
        """'Machine-specific' means THIS machine's root or home, not anything
        that looks like an absolute path. Historical evidence naming some other
        machine is never rewritten to satisfy a packaging check."""
        target = self.repo / "archive" / "proposed-v0.1" / "GENERIC-EXAMPLE.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "Historical examples retained verbatim: `/mnt/user-data/outputs`,\n"
            "`C:/Windows/system.ini`, `/home/example/project`, and\n"
            "`D:/Builds/some-other-repo`.\n",
            encoding="utf-8", newline="\n")
        built = self.build()
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        archive = next((self.repo / "dist").glob("*.zip"))
        checked = self.check("--archive", f"dist/{archive.name}")
        self.assertEqual(checked.returncode, 0, checked.stdout)

    def test_real_source_tree_builds_and_passes_with_archive_scanned(self):
        built = self.build()
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        archive = next((self.repo / "dist").glob("*.zip"))
        checked = self.check("--archive", f"dist/{archive.name}")
        self.assertEqual(checked.returncode, 0, checked.stdout)


# --------------------------------------------------------------------------
# Source-check / builder parity (RFI-23)
#
# The builder scans the packageable source tree for this machine's own root
# and home before it will produce a candidate. Source-mode
# `check_distribution.py` performed the equivalent scan only inside
# `check_archive()`, which runs only when `--archive` is supplied. The two
# gates never disagreed about the RULE; they disagreed about WHEN it applies.
# A tree the builder refuses could therefore pass the earlier, cheaper check,
# and the defect surfaced later as a cascade across this suite instead of as
# one legible check failure.
#
# This locks the parity through the PUBLIC interface — the checker command
# with no `--archive` — so a future refactor cannot restore the asymmetry
# while keeping the internals green.
# --------------------------------------------------------------------------

class SourceModeMachinePathParityTests(DistributionTestCase):
    """Source-mode checking rejects what the builder refuses (RFI-23)."""

    CARRIER = "NOTES-FIXTURE-machine-path.md"

    def test_source_mode_rejects_a_packageable_machine_path(self):
        """`check_distribution.py` with no `--archive` must fail on a
        packageable text artifact carrying this repository's own root.

        The control run first establishes that the fixture reports no
        machine-path failure, so this asserts the carrier's effect and not
        some unrelated condition the fixture copy happened to inherit.
        """
        control = self.check()
        self.assertNotIn("[machine-path]", control.stdout,
                         f"the fixture already reports a machine path:\n{control.stdout}")

        carrier = self.repo / self.CARRIER
        carrier.write_text(
            f"Scratch note. Built from {self.repo.as_posix()}/checks.\n",
            encoding="utf-8", newline="\n")

        result = self.check()
        self.assert_fails(result, "machine-path")
        self.assertIn(self.CARRIER, result.stdout,
                      f"the offending source path was not named:\n{result.stdout}")
        self.assertIn("machine", result.stdout.lower())


# --------------------------------------------------------------------------
# External build output reporting (RFI-26)
#
# `main()` reported the finished archive with
# `target.relative_to(REPO_ROOT).as_posix()`, which raises ValueError for any
# `--output` outside the repository. The archive is collected, gated, written
# and hashed BEFORE that line runs, so the defect is purely in reporting --
# but it exits 1 with a traceback, so any procedure requiring a temporary
# build outside the repository could not exit zero.
#
# This locks the repaired behaviour through the PUBLIC interface -- the
# builder command with an external `--output` -- and asserts in the same run
# that the machine-path gate still refuses, so a reporting repair can never be
# mistaken for, or quietly become, a relaxation of a packaging gate.
# --------------------------------------------------------------------------

class ExternalOutputPathTests(DistributionTestCase):
    """The builder builds, reports, and exits zero for an output directory
    outside the repository, with every packaging gate still armed (RFI-26)."""

    CARRIER = "NOTES-FIXTURE-external-output.md"

    def build_to(self, output):
        return subprocess.run(
            [sys.executable, str(self.repo / "scripts" / "build_distribution.py"),
             "--output", str(output)],
            capture_output=True, text=True, timeout=300)

    def test_build_into_a_directory_outside_the_repository_reports_and_exits_zero(self):
        external = self.tmp / "external-output"
        self.assertFalse(external.is_relative_to(self.repo),
                         "the fixture output directory must lie outside the repository")

        result = self.build_to(external)

        self.assertEqual(result.returncode, 0,
                         "an external --output must exit zero:\n"
                         f"{result.stdout}\n{result.stderr}")
        self.assertNotIn("Traceback", result.stderr, result.stderr)

        archives = sorted(external.glob("*.zip"))
        self.assertEqual(len(archives), 1,
                         f"expected exactly one archive, got {[p.name for p in archives]}")
        self.assertIn(archives[0].name, result.stdout,
                      f"the summary did not name the archive it wrote:\n{result.stdout}")

        checked = self.check("--archive", str(archives[0]))
        self.assertEqual(checked.returncode, 0, checked.stdout)

        # The repair is reporting-only. With the same external --output, a
        # packageable carrier of this fixture's own root must still be refused.
        (self.repo / self.CARRIER).write_text(
            f"Scratch note. Built from {self.repo.as_posix()}/checks.\n",
            encoding="utf-8", newline="\n")
        refused = self.build_to(self.tmp / "external-output-2")
        self.assertNotEqual(refused.returncode, 0,
                            "the machine-path gate was weakened by the repair:\n"
                            f"{refused.stdout}\n{refused.stderr}")
        self.assertIn(self.CARRIER, refused.stdout + refused.stderr,
                      f"the offending path was not named:\n{refused.stdout}{refused.stderr}")


# --------------------------------------------------------------------------
# Adopted-state portability (RFI-17)
#
# `governance/` ships only once a project is adopted. A host absolute path
# inside a governance record is therefore invisible to every pre-adoption gate
# and surfaces for the first time in that project's first adopted build, as a
# refusal. These tests move that discovery earlier.
# --------------------------------------------------------------------------

MACHINE_TEXT_SUFFIXES = (".json", ".md", ".py", ".sh", ".txt", ".yml", ".yaml", ".toml")

# A value that names a filesystem location rather than the repository:
# a POSIX root, a Windows drive, or a UNC share.
ABSOLUTE_VALUE_RE = re.compile(r"^(/|\\\\|[A-Za-z]:[\\/])")


def machine_needles() -> set[str]:
    """This machine's own root and home, in both path flavours.

    The same set the checker builds. Paths of three characters or fewer are
    dropped, because a bare drive root would match almost any text.
    """
    home = Path.home()
    needles = {str(REPO_ROOT), REPO_ROOT.as_posix(), str(home), home.as_posix()}
    return {n for n in needles if len(n) > 3}


class AdoptedStateProjectionTests(DistributionTestCase):
    """A synthetic adopted-state projection, built and checked end to end.

    The fixture writes its own completed work order under history and asserts
    nothing about any live work order's filename or lifecycle stage, so an
    Owner issuance, rename, or removal cannot make it stale (RFI-12). A
    COMPLETE record under the live work-order directory would itself be
    transient release state; closeout moves completed records to history.
    """

    FIXTURE_WO = "governance/history/WO-FIXTURE-portability.md"

    def projection(self, repository_value):
        """An adopted fixture carrying one work order with the given value."""
        adopt_fixture(self.repo)
        target = self.repo / self.FIXTURE_WO
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "---\n"
            "id: WO-FIXTURE\n"
            "status: COMPLETE\n"
            f"repository: {repository_value}\n"
            "doctrine_rev: 0.6\n"
            "---\n"
            "\n"
            "# WO-FIXTURE: synthetic packaging fixture\n"
            "\n"
            "Not a real work order. It exists to exercise the machine-path rule\n"
            "against a governance record that ships only in the adopted state.\n",
            encoding="utf-8", newline="\n")
        return target

    # --- 1. an adopted projection carrying a host path is rejected ---------

    def test_host_path_in_an_adopted_work_order_refuses_the_build(self):
        self.projection(self.repo.as_posix())
        result = self.build()
        output = (result.stdout + result.stderr).replace("\\", "/")
        self.assertNotEqual(
            result.returncode, 0,
            f"the builder produced an adopted candidate carrying a host "
            f"path:\n{output}")
        self.assertIn(self.FIXTURE_WO, output)
        self.assertFalse(list((self.repo / "dist").glob("*.zip")),
                         "a candidate archive was created despite the refusal")

    def test_host_home_path_in_an_adopted_work_order_refuses_the_build(self):
        self.projection(f"{Path.home().as_posix()}/Projects/example")
        result = self.build()
        output = (result.stdout + result.stderr).replace("\\", "/")
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn(self.FIXTURE_WO, output)

    def test_adopted_archive_carrying_a_host_path_fails_the_archive_check(self):
        """The checker gate, independently of the builder preflight."""
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        entry = "writwall/" + self.FIXTURE_WO
        with zipfile.ZipFile(out / "writwall-0.6.zip", "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
            archive.writestr(entry, f"repository: {self.repo.as_posix()}\n")
        result = self.check("--archive", "dist/writwall-0.6.zip")
        self.assert_fails(result, "archive")
        self.assertIn(entry, result.stdout)
        self.assertIn("build machine's own path", result.stdout)

    # --- 2. the same projection with the semantic value passes -------------

    def test_semantic_repository_value_builds_and_checks_clean(self):
        self.projection("this repository, as the session project root")
        built = self.build()
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        archive = next((self.repo / "dist").glob("*.zip"))
        with zipfile.ZipFile(archive) as handle:
            names = handle.namelist()
        self.assertIn("writwall/" + self.FIXTURE_WO, names,
                      "the adopted projection did not ship the work order")
        checked = self.check("--archive", f"dist/{archive.name}")
        self.assertEqual(checked.returncode, 0, checked.stdout)

    # --- 4. the gates this must not weaken ---------------------------------

    def test_adopted_projection_still_refuses_a_lingering_proposed_document(self):
        """RFI-14 coverage survives: the semantic value does not buy an
        exemption from proposed-status detection."""
        self.projection("this repository, as the session project root")
        lingering = self.repo / "governance" / "work-orders" / "WO-FIXTURE-later.md"
        lingering.write_text(
            "---\nid: WO-FIXTURE-LATER\nstatus: proposed\n---\n\nDraft.\n",
            encoding="utf-8", newline="\n")
        result = self.build()
        output = (result.stdout + result.stderr).replace("\\", "/")
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("PROPOSED", output)

    def test_adopted_projection_still_scans_the_shipped_archive_subtree(self):
        """RFI-15 coverage survives: no packageable subtree is exempt, and
        adopting does not introduce a new exemption."""
        self.projection("this repository, as the session project root")
        leak = self.repo / "archive" / "pre-adoption-bootstrap" / "LEAK.md"
        leak.parent.mkdir(parents=True, exist_ok=True)
        leak.write_text(f"root: {self.repo.as_posix()}\n",
                        encoding="utf-8", newline="\n")
        result = self.build()
        output = (result.stdout + result.stderr).replace("\\", "/")
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("archive/pre-adoption-bootstrap/LEAK.md", output)

    def test_pre_adoption_still_excludes_governance_entirely(self):
        """Pre-adoption behaviour is unchanged by any of the above."""
        archive_path = None
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        archive_path = next((self.repo / "dist").glob("*.zip"))
        with zipfile.ZipFile(archive_path) as handle:
            names = handle.namelist()
        self.assertFalse([n for n in names if n.startswith("writwall/governance/")],
                         "governance/ shipped in a pre-adoption archive")


class RealTreeAdoptedPortabilityTests(unittest.TestCase):
    """The real repository, not a relocated copy.

    A fixture copy cannot see this defect. The machine-path needles are the
    *checked* tree's own root and the building user's home, so once the tree is
    copied into a temporary directory this machine's real path becomes a
    foreign absolute path — which the rule deliberately allows, and must keep
    allowing, because historical evidence naming some other machine is never
    rewritten to satisfy a packaging check. Only a scan rooted at the real
    REPO_ROOT observes what the first adopted build here would refuse.
    """

    def collect(self, state_attribute):
        """The builder's own file collection for a governance state.

        Imported with bytecode writes suppressed: `scripts/` is not a granted
        cache location, and a test must not leave one behind.
        """
        original = sys.dont_write_bytecode
        scripts = str(REPO_ROOT / "scripts")
        sys.dont_write_bytecode = True
        sys.path.insert(0, scripts)
        try:
            import build_distribution as builder
            return builder.collect_files(getattr(builder, state_attribute))
        finally:
            if scripts in sys.path:
                sys.path.remove(scripts)
            sys.dont_write_bytecode = original

    def carriers(self, files):
        builder = load_distribution_builder()
        needles = machine_needles()
        found = []
        for path in files:
            if path.suffix.lower() not in MACHINE_TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for number, line in enumerate(text.splitlines(), 1):
                if any(builder.machine_path_occurs(line, needle)
                       for needle in needles):
                    found.append(
                        f"{path.relative_to(REPO_ROOT).as_posix()}:{number}")
        return found

    # --- 3. the current repository's adopted collection --------------------

    def test_adopted_collection_carries_no_host_path(self):
        carriers = self.carriers(self.collect("ADOPTED"))
        self.assertEqual(
            carriers, [],
            "these files ship in the adopted state and carry this machine's "
            "own path, so the first adopted build refuses:\n  "
            + "\n  ".join(carriers))

    def test_pre_adoption_collection_carries_no_host_path(self):
        carriers = self.carriers(self.collect("PRE_ADOPTION"))
        self.assertEqual(carriers, [], "\n  ".join(carriers))

    def test_adopting_only_ever_adds_files(self):
        """Guards the premise of the test above: the adopted collection is a
        superset, so scanning it covers the pre-adoption one as well."""
        pre = set(self.collect("PRE_ADOPTION"))
        adopted = set(self.collect("ADOPTED"))
        self.assertTrue(pre <= adopted,
                        sorted(str(p) for p in pre - adopted))
        self.assertTrue(any(p.parts[-2:][0] != "" and "governance" in p.parts
                            for p in adopted - pre),
                        "the adopted collection added no governance file")

    # --- the durable convention, without live-filename coupling ------------

    def test_no_governance_record_declares_an_absolute_repository_value(self):
        """Charter A.6: if a work order carries `repository:` metadata, its
        value is a semantic identifier, never a host absolute path.

        Stated over whatever governance records exist, so issuing, renaming, or
        removing one cannot make this assertion stale.
        """
        offenders = []
        for path in sorted((REPO_ROOT / "governance").rglob("*.md")):
            if not path.is_file():
                continue
            for number, line in enumerate(
                    path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                if not line.startswith("repository:"):
                    continue
                value = line.split(":", 1)[1].strip().strip("'\"")
                if ABSOLUTE_VALUE_RE.match(value):
                    offenders.append(
                        f"{path.relative_to(REPO_ROOT).as_posix()}:{number}")
        self.assertEqual(offenders, [],
                         "absolute `repository:` values:\n  " + "\n  ".join(offenders))


class TransientReleaseStateTests(DistributionTestCase):
    """WO-PL-015: a release candidate is a between-work-order checkpoint, never
    an in-progress implementation envelope. Source checking, distribution
    building, and archive checking must all fail closed while an activation
    pointer, a live work-order file, or a live report file is present."""

    def make_adopted(self):
        adopt_fixture(self.repo)

    def clear_live_dirs(self):
        """Return the fixture to the clean between-work-orders state.

        The fixture is a copy of the real repository, so without this the
        live repository's own in-progress work order and activation pointer
        leak into every test below, exactly the RFI-12-style coupling
        `pre_adoption_fixture` already guards against for governance state.
        """
        clear_transient_release_state(self.repo)

    def write_active_work_order(self, name="WO-999-FIXTURE.md"):
        wo = self.repo / "governance" / "work-orders" / name
        wo.write_text("---\nstatus: ACTIVE\n---\n\n# WO-999\n",
                      encoding="utf-8", newline="\n")
        return wo

    def write_pointer(self, target="governance/work-orders/WO-999-FIXTURE.md"):
        pointer = self.repo / ".claude" / "active-wo.txt"
        pointer.parent.mkdir(parents=True, exist_ok=True)
        pointer.write_text(target, encoding="utf-8", newline="\n")
        return pointer

    def write_report(self, name="WO-999-REPORT.md"):
        report = self.repo / "governance" / "reports" / name
        report.write_text("# report\n", encoding="utf-8", newline="\n")
        return report

    # --- source mode --------------------------------------------------

    def test_source_check_fails_with_pointer_only(self):
        self.make_adopted()
        self.clear_live_dirs()
        self.write_pointer()
        self.assert_fails(self.check(), "transient-release-state")

    def test_source_check_fails_with_live_work_order_only(self):
        self.make_adopted()
        self.clear_live_dirs()
        self.write_active_work_order()
        self.assert_fails(self.check(), "transient-release-state")

    def test_source_check_fails_with_live_report_only(self):
        self.make_adopted()
        self.clear_live_dirs()
        self.write_report()
        self.assert_fails(self.check(), "transient-release-state")

    def test_source_check_fails_with_nested_live_work_order(self):
        self.make_adopted()
        self.clear_live_dirs()
        nested = self.repo / "governance" / "work-orders" / "sub" / "WO-999.md"
        nested.parent.mkdir(parents=True)
        nested.write_text("# nested\n", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "transient-release-state")

    def test_gitkeep_placeholders_do_not_trip_the_gate(self):
        self.make_adopted()
        self.clear_live_dirs()
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_nested_gitkeep_under_work_orders_is_transient(self):
        """Only the two tracked root `.gitkeep` files are exempt. A
        `.gitkeep` nested under a subdirectory is not a tracked repository
        placeholder — nothing tracks one — so it is ordinary transient
        content, exactly like any other file placed under a live directory."""
        self.make_adopted()
        self.clear_live_dirs()
        nested = self.repo / "governance" / "work-orders" / "sub" / ".gitkeep"
        nested.parent.mkdir(parents=True)
        nested.write_text("", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "transient-release-state")

    def test_nested_gitkeep_under_reports_is_transient(self):
        self.make_adopted()
        self.clear_live_dirs()
        nested = self.repo / "governance" / "reports" / "sub" / ".gitkeep"
        nested.parent.mkdir(parents=True)
        nested.write_text("", encoding="utf-8", newline="\n")
        self.assert_fails(self.check(), "transient-release-state")

    def test_exact_tracked_root_gitkeeps_pass_while_nested_ones_fail(self):
        """The two exact tracked roots and a nested same-named file are
        classified differently by exactly one exemption, in one run."""
        self.make_adopted()
        self.clear_live_dirs()
        nested_wo = self.repo / "governance" / "work-orders" / "sub" / ".gitkeep"
        nested_wo.parent.mkdir(parents=True)
        nested_wo.write_text("", encoding="utf-8", newline="\n")
        result = self.check()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("[transient-release-state]", result.stdout)
        self.assertNotIn("governance/work-orders/.gitkeep", result.stdout)
        self.assertIn("governance/work-orders/sub/.gitkeep", result.stdout)

    def test_completed_history_record_is_not_classified_transient(self):
        self.make_adopted()
        self.clear_live_dirs()
        history = self.repo / "governance" / "history" / "WO-999-COMPLETE.md"
        history.parent.mkdir(parents=True, exist_ok=True)
        history.write_text("# WO-999 was ACTIVE when issued\n",
                           encoding="utf-8", newline="\n")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_quoted_active_prose_elsewhere_is_not_classified_transient(self):
        """No generic substring match on ACTIVE prose: a document that merely
        quotes the word must not trip the gate."""
        self.make_adopted()
        self.clear_live_dirs()
        self.edit("CONTRIBUTING.md", "Thank you for helping improve Writwall.",
                  "This repository quotes the word ACTIVE in ordinary prose. "
                  "Thank you for helping improve Writwall.")
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_all_variants_aggregate_in_one_run(self):
        """The checker aggregates every transient path rather than stopping at
        the first category it finds."""
        self.make_adopted()
        self.clear_live_dirs()
        self.write_pointer()
        self.write_active_work_order()
        self.write_report()
        result = self.check()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout.count("[transient-release-state]"), 3,
                         result.stdout)

    # --- builder / build mode ------------------------------------------

    def test_builder_refuses_before_writing_an_archive(self):
        self.make_adopted()
        self.clear_live_dirs()
        self.write_active_work_order()
        self.write_pointer()
        self.write_report()
        result = self.build()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("transient", (result.stderr + result.stdout).lower())
        self.assertEqual(list((self.repo / "dist").glob("*.zip")), [],
                         "the builder wrote an archive despite live transient state")

    def test_clean_adopted_fixture_builds_and_passes(self):
        self.make_adopted()
        self.clear_live_dirs()
        self.assertEqual(self.check().returncode, 0, self.check().stdout)
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_clean_pre_adoption_lockout_fixture_builds_and_passes(self):
        """Clean pre-adoption lockout state (the ordinary state on a fresh
        adopter clone, and between this repository's own work orders) must
        remain buildable."""
        self.clear_live_dirs()
        self.assertEqual(self.check().returncode, 0, self.check().stdout)
        result = self.build()
        self.assertEqual(result.returncode, 0, result.stderr)

    # --- archive mode ----------------------------------------------------

    def build_hand_archive(self, extra_entries):
        """A hand-built archive satisfying every OTHER adopted-state archive
        check, so a `[transient-release-state]` (or its absence) is the only
        thing a test using this fixture is actually exercising.

        The adopted state independently requires exactly two `.claude/`
        members (`ClaudeDirPackagingTests`): `.claude/settings.json` and
        `.claude/hooks/wo_capability_wall.py`. Omitting them makes `check()`
        fail on `[archive]` for a reason unrelated to WO-PL-015, which would
        make a passing-fixture test (like the `.gitkeep`-members test) fail
        for the wrong reason instead of proving what it claims to prove.
        """
        self.make_adopted()
        self.clear_live_dirs()
        out = self.repo / "dist"
        out.mkdir(exist_ok=True)
        path = out / "writwall-0.6.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("writwall/README.md", "x")
            archive.writestr("writwall/CLAUDE.md", "x")
            archive.writestr("writwall/MANIFEST.sha256", "x")
            archive.writestr("writwall/governance/decisions/DR-001.md", "x")
            archive.writestr("writwall/.claude/settings.json", "{}")
            archive.writestr("writwall/.claude/hooks/wo_capability_wall.py", "x")
            for name, content in extra_entries.items():
                archive.writestr(name, content)
        return path

    def test_archive_carrying_the_pointer_fails(self):
        self.build_hand_archive({"writwall/.claude/active-wo.txt": "x"})
        self.assert_fails(
            self.check("--archive", "dist/writwall-0.6.zip"), "transient-release-state")

    def test_archive_carrying_a_live_work_order_member_fails(self):
        self.build_hand_archive(
            {"writwall/governance/work-orders/WO-999.md": "x"})
        self.assert_fails(
            self.check("--archive", "dist/writwall-0.6.zip"), "transient-release-state")

    def test_archive_carrying_a_nested_live_work_order_member_fails(self):
        self.build_hand_archive(
            {"writwall/governance/work-orders/sub/WO-999.md": "x"})
        self.assert_fails(
            self.check("--archive", "dist/writwall-0.6.zip"), "transient-release-state")

    def test_archive_carrying_a_live_report_member_fails(self):
        self.build_hand_archive(
            {"writwall/governance/reports/WO-999-REPORT.md": "x"})
        self.assert_fails(
            self.check("--archive", "dist/writwall-0.6.zip"), "transient-release-state")

    def test_archive_gitkeep_members_pass(self):
        self.build_hand_archive({
            "writwall/governance/work-orders/.gitkeep": "",
            "writwall/governance/reports/.gitkeep": "",
        })
        result = self.check("--archive", "dist/writwall-0.6.zip")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_archive_nested_gitkeep_member_under_work_orders_fails(self):
        self.build_hand_archive({
            "writwall/governance/work-orders/sub/.gitkeep": "",
        })
        self.assert_fails(
            self.check("--archive", "dist/writwall-0.6.zip"), "transient-release-state")

    def test_archive_nested_gitkeep_member_under_reports_fails(self):
        self.build_hand_archive({
            "writwall/governance/reports/sub/.gitkeep": "",
        })
        self.assert_fails(
            self.check("--archive", "dist/writwall-0.6.zip"), "transient-release-state")

    # --- the observed WO-PL-014 build, deterministically before/after ------

    def test_the_wo_pl_014_style_live_build_is_now_refused(self):
        """The exact live-state build observed during WO-PL-014: an ACTIVE
        work order and its live report both present while adopted."""
        self.make_adopted()
        self.clear_live_dirs()
        self.write_active_work_order()
        self.write_pointer()
        self.write_report()
        check_result = self.check()
        self.assertNotEqual(check_result.returncode, 0, check_result.stdout)
        build_result = self.build()
        self.assertNotEqual(build_result.returncode, 0, build_result.stdout)
        self.assertEqual(list((self.repo / "dist").glob("*.zip")), [])

    # --- regression: one canonical classifier -------------------------

    def test_checker_consumes_the_builders_classifier_rather_than_restating_it(self):
        checker_text = (REPO_ROOT / "checks" / "check_distribution.py").read_text(
            encoding="utf-8")
        for name in ("ACTIVATION_POINTER", "LIVE_WORK_ORDER_DIR", "LIVE_REPORT_DIR"):
            self.assertNotIn(
                f"{name} =", checker_text,
                f"checker restates {name} instead of consuming the builder's "
                "single definition, drifting into a second deny list")

    def test_builder_and_checker_agree_on_every_transient_path(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_wopl015_builder", REPO_ROOT / "scripts" / "build_distribution.py")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)

        spec2 = importlib.util.spec_from_file_location(
            "_wopl015_checker", REPO_ROOT / "checks" / "check_distribution.py")
        checker = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(checker)
        checker_builder = checker.load_builder()

        samples = [
            ".claude/active-wo.txt",
            "governance/work-orders/WO-999.md",
            "governance/work-orders/.gitkeep",
            "governance/work-orders/sub/WO-999.md",
            "governance/work-orders/sub/.gitkeep",
            "governance/reports/WO-999-REPORT.md",
            "governance/reports/.gitkeep",
            "governance/reports/sub/.gitkeep",
            "governance/history/WO-999-COMPLETE.md",
            "README.md",
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                self.assertEqual(
                    builder.is_transient_release_path(sample),
                    checker_builder.is_transient_release_path(sample))


class DocumentationTruthTests(DistributionTestCase):
    """WO-PL-022 B.3 item 6: the documentation-truth rule must fail
    deterministically, through the existing distribution check surface, when
    the evidence-backed public pilot example required by B.3 item 5 is
    missing from the source tree."""

    def test_missing_pilot_example_fails_doc_truth(self):
        pilot_example = self.repo / "examples" / "plumbline-self-hosting-pilot.md"
        pilot_example.unlink(missing_ok=True)
        self.assertFalse(pilot_example.is_file(),
                         "fixture must not have the pilot example")
        result = self.check()
        self.assert_fails(result, "doc-truth")
        self.assertIn("example", result.stdout.lower())

    def test_pilot_example_missing_provider_envelope_disclosure_fails_doc_truth(self):
        """B.3 item 4: the pilot example must foreground that WO-PL-017
        through WO-PL-020 ran in Codex outside the installed Claude hook and
        were instruction-bounded. A pilot example present but silent on that
        provider envelope is still an undisclosed evidence-scope gap, not a
        missing-example gap, so it must fail doc-truth for a distinct reason.
        """
        examples_dir = self.repo / "examples"
        examples_dir.mkdir(exist_ok=True)
        (examples_dir / "plumbline-self-hosting-pilot.md").write_text(
            "# Writwall self-hosting pilot\n\n"
            "A pilot example that omits the provider-envelope disclosure "
            "required by B.3 item 4.\n",
            encoding="utf-8", newline="\n")
        result = self.check()
        self.assert_fails(result, "doc-truth")
        combined = result.stdout.lower()
        self.assertIn("provider envelope", combined)
        self.assertNotIn("missing evidence-backed public pilot example", combined)

    def test_pilot_example_claiming_full_enforcement_fails_doc_truth(self):
        """B.3 item 6, unsupported-evidence-claims case.

        The accepted aggregate evidence (DR-002's deterministic pilot result;
        STATE.md's per-order Declared/enforced/unenforced rows, e.g. 8 / 0 / 8
        for WO-PL-016) records that zero whole surfaces qualified as
        mechanically enforced under the strict complete-channel metric in
        every counted pilot order. A pilot example asserting full mechanical
        enforcement with no unenforced boundary therefore overclaims what the
        accepted aggregate record supports, independent of any private
        transactional history.

        The fixture satisfies the missing-example and provider-envelope
        checks so only the new, distinct overclaim reason can fail here.
        """
        examples_dir = self.repo / "examples"
        examples_dir.mkdir(exist_ok=True)
        (examples_dir / "plumbline-self-hosting-pilot.md").write_text(
            "# Writwall self-hosting pilot\n\n"
            "WO-PL-017 through WO-PL-020 ran in Codex, outside the installed "
            "Claude hook, and were instruction-bounded.\n\n"
            "Every declared capability surface was mechanically enforced, "
            "with zero unenforced boundaries across the pilot.\n",
            encoding="utf-8", newline="\n")
        result = self.check()
        self.assert_fails(result, "doc-truth")
        combined = result.stdout.lower()
        self.assertIn("unsupported", combined)
        self.assertNotIn("missing evidence-backed public pilot example", combined)
        self.assertNotIn("provider envelope", combined)


class DayZeroCoordinatorContractTests(DistributionTestCase):
    """WO-PL-040: the executable front door and all human routes stay aligned."""

    def test_clean_tree_carries_the_day_zero_contract(self):
        result = self.check()
        self.assertNotIn("[onboarding]", result.stdout)
        for relpath in (
            "docs/day-zero-coordinator.md",
            "scripts/start_writwall.py",
            "tests/test_start_writwall.py",
        ):
            self.assertTrue((self.repo / relpath).is_file(), relpath)

    def test_readme_losing_single_entry_command_fails(self):
        self.edit("README.md", "scripts/start_writwall.py", "scripts/manual-start.py",
                  count=-1)
        self.assert_fails(self.check(), "onboarding")

    def test_start_here_losing_temporary_bundle_fails(self):
        self.edit("START-HERE.md", ".writwall-bootstrap/", ".temporary-bootstrap/")
        self.assert_fails(self.check(), "onboarding")

    def test_skill_losing_repository_state_rule_fails(self):
        self.edit(
            "skills/writwall-adopt/SKILL.md",
            "Never infer an active work order from prior chat",
            "Use the work order remembered from prior chat",
        )
        self.assert_fails(self.check(), "onboarding")

    def test_coordinator_reference_losing_authority_boundary_fails(self):
        self.edit(
            "docs/day-zero-coordinator.md",
            "confers no authority",
            "is an authorization",
        )
        self.assert_fails(self.check(), "onboarding")


if __name__ == "__main__":
    unittest.main()
