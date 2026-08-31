# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Narrowly routed distribution assertion for WO-PL-014.

Asserts that checks/check_work_order_dispatch.py and its test module are
declared required and packageable by checks/check_distribution.py. This is
deliberately separate from tests/test_distribution.py's broader suite: it
exists to pin exactly the WO-PL-014 checker/test pair to the distribution
gate, not to duplicate that suite's general coverage.

Standard library only. Each test copies the repository into its own
temporary directory and mutates the copy, so the assertion is observed
firing rather than assumed.
"""
from __future__ import annotations

import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "dist", "__pycache__", ".pytest_cache", "bootstrap"}

NEW_REQUIRED_FILES = (
    "checks/check_work_order_dispatch.py",
    "tests/test_check_work_order_dispatch.py",
)

BUNDLE_CHECKER_RELPATH = "skills/writwall-adopt/assets/checks/check_work_order_dispatch.py"

NAME_CLEARANCE_BUNDLE_COPIES = {
    "skills/writwall-adopt/assets/scripts/collect_name_clearance.py":
        "scripts/collect_name_clearance.py",
    "skills/writwall-adopt/assets/checks/check_name_clearance.py":
        "checks/check_name_clearance.py",
    "skills/writwall-adopt/references/name-clearance.md":
        "docs/name-clearance.md",
}

LICENSE_RECORDS = (
    "LICENSE",
    "LICENSES/CC-BY-4.0.txt",
    "LICENSES/CC0-1.0.txt",
    "LICENSES/MIT-0.txt",
    "LICENSES/Apache-2.0.txt",
    "LICENSE-MAP.md",
    "NAMING.md",
    "CONTRIBUTING.md",
    "decisions/DR-003.md",
    "skills/writwall-adopt/LICENSE-MAP.md",
)

LICENSE_CURRENT_DOCUMENTS = (
    "LICENSE-MAP.md",
    "NAMING.md",
    "CONTRIBUTING.md",
    "decisions/DR-003.md",
    "skills/writwall-adopt/LICENSE-MAP.md",
)

PROJECTION_REQUIRED_FILES = (
    "PUBLICATION.md",
    "projection/public-files.txt",
    "scripts/build_public_projection.py",
    "checks/check_public_projection.py",
    "tests/test_public_projection.py",
)

DAY_ZERO_REQUIRED_FILES = (
    "checks/check_coordinator_release.py",
    "docs/day-zero-coordinator.md",
    "docs/architect-interview.md",
    "pyproject.toml",
    "scripts/start_writwall.py",
    "tests/test_start_writwall.py",
    "tests/test_coordinator_release.py",
    "writwall_cli/__init__.py",
    "writwall_cli/__main__.py",
    "writwall_cli/coordinator.py",
)


class DispatchCheckerPackagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "writwall"
        shutil.copytree(REPO_ROOT, self.repo, ignore=shutil.ignore_patterns(*SKIP_DIRS),
                        dirs_exist_ok=True)

    def check(self, *args):
        return subprocess.run(
            [sys.executable, str(self.repo / "checks" / "check_distribution.py"), *args],
            capture_output=True, text=True, timeout=300)

    def build_projection(self) -> Path:
        candidate = self.tmp / "candidate"
        patterns = self.tmp / "patterns.txt"
        patterns.write_text("PRIVATE_" + "NEEDLE\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-B",
             str(self.repo / "scripts" / "build_public_projection.py"),
             "--source-root", str(self.repo), "--output", str(candidate),
             "--private-pattern-file", str(patterns)],
            capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return candidate

    def build_projection_archive(self, candidate: Path) -> Path:
        output = self.tmp / "archive-output"
        result = subprocess.run(
            [sys.executable, "-B",
             str(candidate / "scripts" / "build_distribution.py"),
             "--output", str(output)],
            cwd=candidate, capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return next(output.glob("*.zip"))

    def test_projection_mode_requires_projection_records(self):
        shutil.rmtree(self.repo / "archive", ignore_errors=True)
        (self.repo / "PROJECTION-MANIFEST.sha256").unlink(missing_ok=True)
        (self.repo / "PROJECTION-PROVENANCE.md").unlink(missing_ok=True)
        result = self.check("--projection")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("unrecognized arguments", result.stderr)
        self.assertIn("[projection]", result.stdout)
        self.assertIn("PROJECTION-PROVENANCE.md", result.stdout)

    def test_projection_mode_does_not_claim_private_archive_provenance(self):
        shutil.rmtree(self.repo / "archive", ignore_errors=True)
        (self.repo / "projection").mkdir(exist_ok=True)
        (self.repo / "projection" / "public-files.txt").write_text(
            "README.md\n", encoding="utf-8")
        (self.repo / "PROJECTION-MANIFEST.sha256").write_text("fixture\n", encoding="utf-8")
        (self.repo / "PROJECTION-PROVENANCE.md").write_text(
            "private governed source\n", encoding="utf-8")
        result = self.check("--projection")
        self.assertNotIn("[required-file] missing: archive/README.md", result.stdout)
        self.assertNotIn("[v0.1]", result.stdout)
        self.assertNotIn("[provenance]", result.stdout)

    def test_onboarding_contract_fails_when_first_prompt_drifts(self):
        start = self.repo / "START-HERE.md"
        text = start.read_text(encoding="utf-8")
        start.write_text(
            text.replace("Act as my Writwall adoption coordinator",
                         "Act as my generic helper"),
            encoding="utf-8",
            newline="\n",
        )

        result = self.check()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[onboarding]", result.stdout)
        self.assertIn("START-HERE.md", result.stdout)

    def test_onboarding_contract_fails_when_probe_safety_drifts(self):
        adapter = self.repo / "adapters" / "claude-code" / "README.md"
        text = adapter.read_text(encoding="utf-8")
        adapter.write_text(
            text.replace("explicit disposable fixture", "external target", 1),
            encoding="utf-8",
            newline="\n",
        )

        result = self.check()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[onboarding]", result.stdout)
        self.assertIn("adapters/claude-code/README.md", result.stdout)

    def test_projection_mode_validates_projection_manifest_contents(self):
        candidate = self.build_projection()
        manifest = candidate / "PROJECTION-MANIFEST.sha256"
        lines = manifest.read_text(encoding="utf-8").splitlines()
        lines[0] = "0" * 64 + lines[0][64:]
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-B",
             str(candidate / "checks" / "check_distribution.py"), "--projection"],
            cwd=candidate, capture_output=True, text=True, timeout=300)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[projection]", result.stdout)

    def test_projection_mode_validates_projection_provenance_contents(self):
        candidate = self.build_projection()
        (candidate / "PROJECTION-PROVENANCE.md").write_bytes(b"not provenance\n")
        result = subprocess.run(
            [sys.executable, "-B",
             str(candidate / "checks" / "check_distribution.py"), "--projection"],
            cwd=candidate, capture_output=True, text=True, timeout=300)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[projection]", result.stdout)

    def test_projection_archive_rejects_private_history_member(self):
        candidate = self.build_projection()
        archive = self.build_projection_archive(candidate)
        with zipfile.ZipFile(archive, "a") as handle:
            handle.writestr("writwall/governance/history/secret.md", "secret\n")
        result = subprocess.run(
            [sys.executable, "-B",
             str(candidate / "checks" / "check_distribution.py"),
             "--projection", "--archive", str(archive)],
            cwd=candidate, capture_output=True, text=True, timeout=300)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[projection]", result.stdout)

    def test_projection_archive_rejects_unknown_member(self):
        candidate = self.build_projection()
        archive = self.build_projection_archive(candidate)
        with zipfile.ZipFile(archive, "a") as handle:
            handle.writestr("writwall/unknown.txt", "unknown\n")
        result = subprocess.run(
            [sys.executable, "-B",
             str(candidate / "checks" / "check_distribution.py"),
             "--projection", "--archive", str(archive)],
            cwd=candidate, capture_output=True, text=True, timeout=300)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[projection]", result.stdout)

    def test_projection_archive_rejects_duplicate_member(self):
        candidate = self.build_projection()
        archive = self.build_projection_archive(candidate)
        with zipfile.ZipFile(archive, "a") as handle:
            handle.writestr("writwall/README.md", "duplicate\n")
        result = subprocess.run(
            [sys.executable, "-B",
             str(candidate / "checks" / "check_distribution.py"),
             "--projection", "--archive", str(archive)],
            cwd=candidate, capture_output=True, text=True, timeout=300)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[projection]", result.stdout)
        self.assertIn("duplicate", result.stdout.lower())

    def test_projection_archive_rejects_unsafe_member_path(self):
        candidate = self.build_projection()
        archive = self.build_projection_archive(candidate)
        with zipfile.ZipFile(archive, "a") as handle:
            handle.writestr("writwall/../escape.txt", "escape\n")
        result = subprocess.run(
            [sys.executable, "-B",
             str(candidate / "checks" / "check_distribution.py"),
             "--projection", "--archive", str(archive)],
            cwd=candidate, capture_output=True, text=True, timeout=300)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[projection]", result.stdout)

    def test_projection_archive_rejects_empty_denied_directory_member(self):
        candidate = self.build_projection()
        archive = self.build_projection_archive(candidate)
        with zipfile.ZipFile(archive, "a") as handle:
            handle.writestr("writwall/governance/history/", b"")
        result = subprocess.run(
            [sys.executable, "-B",
             str(candidate / "checks" / "check_distribution.py"),
             "--projection", "--archive", str(archive)],
            cwd=candidate, capture_output=True, text=True, timeout=300)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("[projection]", result.stdout)

    def test_projection_archive_rejects_symlink_member(self):
        candidate = self.build_projection()
        archive = self.build_projection_archive(candidate)
        link = zipfile.ZipInfo("writwall/link")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(archive, "a") as handle:
            handle.writestr(link, "README.md")
        result = subprocess.run(
            [sys.executable, "-B",
             str(candidate / "checks" / "check_distribution.py"),
             "--projection", "--archive", str(archive)],
            cwd=candidate, capture_output=True, text=True, timeout=300)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("symlink", result.stdout.lower())

    def test_projection_toolset_is_required_by_the_source_gate(self):
        for relpath in PROJECTION_REQUIRED_FILES:
            with self.subTest(relpath=relpath):
                target = self.repo / relpath
                original = target.read_bytes()
                target.unlink()
                try:
                    result = self.check()
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(f"[required-file] missing: {relpath}", result.stdout)
                finally:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(original)

    def test_dispatch_checker_and_test_are_required(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_check_distribution", REPO_ROOT / "checks" / "check_distribution.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name in NEW_REQUIRED_FILES:
            self.assertIn(name, module.REQUIRED_FILES,
                          f"{name} is not in check_distribution.py REQUIRED_FILES")

    def test_day_zero_coordinator_files_are_required(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_check_distribution_day_zero",
            REPO_ROOT / "checks" / "check_distribution.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name in DAY_ZERO_REQUIRED_FILES:
            self.assertIn(name, module.REQUIRED_FILES,
                          f"{name} is not required by the distribution gate")

    def test_missing_day_zero_coordinator_file_fails_distribution_gate(self):
        for relpath in DAY_ZERO_REQUIRED_FILES:
            with self.subTest(relpath=relpath):
                target = self.repo / relpath
                original = target.read_bytes()
                target.unlink()
                try:
                    result = self.check()
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(f"[required-file] missing: {relpath}", result.stdout)
                finally:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(original)

    def test_missing_dispatch_checker_fails_distribution_gate(self):
        (self.repo / "checks" / "check_work_order_dispatch.py").unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("[required-file]", result.stdout)
        self.assertIn("check_work_order_dispatch.py", result.stdout)

    def test_missing_dispatch_test_fails_distribution_gate(self):
        (self.repo / "tests" / "test_check_work_order_dispatch.py").unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("[required-file]", result.stdout)
        self.assertIn("test_check_work_order_dispatch.py", result.stdout)

    def test_clean_copy_with_dispatch_pair_present_does_not_fail_on_required_file(self):
        result = self.check()
        self.assertNotIn("check_work_order_dispatch.py is missing", result.stdout)
        self.assertNotIn("[required-file] missing: checks/check_work_order_dispatch.py",
                         result.stdout)
        self.assertNotIn("[required-file] missing: tests/test_check_work_order_dispatch.py",
                         result.stdout)

    def test_bundle_checker_copy_is_declared(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_check_distribution", REPO_ROOT / "checks" / "check_distribution.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        copy_relpaths = {p.relative_to(REPO_ROOT).as_posix() for p in module.BUNDLE_COPIES}
        self.assertIn(BUNDLE_CHECKER_RELPATH, copy_relpaths,
                      "the bundled adoption-skill checker copy is not declared in "
                      "check_distribution.py BUNDLE_COPIES")

    def test_missing_bundle_checker_copy_fails_distribution_gate(self):
        (self.repo / BUNDLE_CHECKER_RELPATH).unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("check_work_order_dispatch.py", result.stdout)

    def test_bundle_checker_copy_drift_fails_distribution_gate(self):
        target = self.repo / BUNDLE_CHECKER_RELPATH
        target.write_bytes(target.read_bytes() + b"\n# local drift\n")
        result = self.check()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("[bundle]", result.stdout)

    def test_clean_copy_with_bundle_checker_present_does_not_fail_on_bundle(self):
        result = self.check()
        self.assertNotIn(f"bundle copy missing: {BUNDLE_CHECKER_RELPATH}", result.stdout)
        self.assertNotIn(f"differs in content from checks/check_work_order_dispatch.py",
                         result.stdout)

    def test_name_clearance_bundle_copies_are_declared_and_drift_checked(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_check_distribution_name_clearance",
            REPO_ROOT / "checks" / "check_distribution.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        declared = {
            copy.relative_to(REPO_ROOT).as_posix():
                source.relative_to(REPO_ROOT).as_posix()
            for copy, source in module.BUNDLE_COPIES.items()
        }
        for copy, source in NAME_CLEARANCE_BUNDLE_COPIES.items():
            self.assertEqual(declared.get(copy), source, copy)

            target = self.repo / copy
            original = target.read_bytes()
            target.unlink()
            missing = self.check()
            self.assertNotEqual(missing.returncode, 0, missing.stdout)
            self.assertIn(f"bundle copy missing: {copy}", missing.stdout)
            target.write_bytes(original + b"\n# drift\n")
            drift = self.check()
            self.assertNotEqual(drift.returncode, 0, drift.stdout)
            self.assertIn(f"{copy} differs in content from {source}", drift.stdout)
            target.write_bytes(original)

    def test_missing_root_license_fails_distribution_gate(self):
        (self.repo / "LICENSE").unlink()
        result = self.check()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("[required-file] missing: LICENSE", result.stdout)

    def test_each_license_record_is_required_by_the_public_gate(self):
        for relpath in LICENSE_RECORDS:
            with self.subTest(relpath=relpath):
                target = self.repo / relpath
                original = target.read_bytes()
                target.unlink()
                try:
                    result = self.check()
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(f"[required-file] missing: {relpath}",
                                  result.stdout)
                finally:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(original)

    def test_root_license_must_match_cc_by_legal_code(self):
        (self.repo / "LICENSE").write_text("drifted\n", encoding="utf-8")
        result = self.check()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("[license] LICENSE differs from LICENSES/CC-BY-4.0.txt",
                      result.stdout)

    def test_bundle_license_map_is_recognized_metadata(self):
        result = self.check()
        self.assertNotIn(
            "skills/writwall-adopt/LICENSE-MAP.md is an unrecognized file",
            result.stdout)

    def test_each_license_prose_record_is_scanned_by_the_public_gate(self):
        forbidden_claim = b"\nv0.1 was ratified\n"
        for relpath in LICENSE_CURRENT_DOCUMENTS:
            with self.subTest(relpath=relpath):
                target = self.repo / relpath
                original = target.read_bytes()
                target.write_bytes(original + forbidden_claim)
                try:
                    result = self.check()
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(f"[v0.1] {relpath} claims 'v0.1 was ratified'",
                                  result.stdout)
                finally:
                    target.write_bytes(original)

    def test_licensing_direction_must_name_ratified_supersession(self):
        path = self.repo / "decisions" / "LICENSING-DIRECTION.md"
        path.write_bytes(path.read_bytes().replace(b"SUPERSEDED", b"ARCHIVED", 1))
        result = self.check()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("[license] decisions/LICENSING-DIRECTION.md lacks the "
                      "DR-003 supersession marker", result.stdout)

    def test_distribution_gate_runs_license_checker(self):
        metadata = self.repo / "REUSE.toml"
        metadata.write_bytes(
            metadata.read_bytes().replace(
                b'"*.md"', b'"README-NOT-PRESENT.md"', 1
            )
        )

        result = self.check()

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(
            "[license-gate] [coverage] README.md has no license declaration",
            result.stdout,
        )


if __name__ == "__main__":
    unittest.main()
