# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Public-interface tests for the coordinator release-candidate gate."""

from __future__ import annotations

import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "checks" / "check_coordinator_release.py"
PUBLIC_FILES = REPO_ROOT / "projection" / "public-files.txt"
REQUIRED_SOURCE = (
    "pyproject.toml",
    "writwall_cli/__init__.py",
    "writwall_cli/__main__.py",
    "writwall_cli/coordinator.py",
    "scripts/start_writwall.py",
    "scripts/privacy_screen.py",
    "skills/writwall-adopt",
)


def load_checker():
    spec = importlib.util.spec_from_file_location("coordinator_release_checker", CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def tree_digest(root: Path) -> str:
    lines: list[str] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {relative}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()


class CoordinatorReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.temp, True)

    def run_checker(self, candidate: Path):
        return subprocess.run(
            [sys.executable, "-B", str(CHECKER), str(candidate)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=240,
        )

    def make_candidate(self) -> Path:
        candidate = self.temp / "candidate"
        candidate.mkdir()
        for relative in REQUIRED_SOURCE:
            source = REPO_ROOT / relative
            target = candidate / relative
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
        return candidate

    def test_missing_candidate_contract_fails_before_build(self):
        candidate = self.temp / "incomplete"
        candidate.mkdir()
        result = self.run_checker(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("candidate contract", result.stdout + result.stderr)
        self.assertIn("pyproject.toml", result.stdout + result.stderr)

    def test_complete_external_candidate_installs_and_emits_full_handoff(self):
        candidate = self.make_candidate()
        before = tree_digest(candidate)
        result = self.run_checker(candidate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK: coordinator release candidate passed", result.stdout)
        self.assertIn("installed command", result.stdout)
        self.assertIn("complete handoff", result.stdout)
        self.assertIn("candidate unchanged", result.stdout)
        self.assertEqual(tree_digest(candidate), before)

    def test_broken_build_backend_fails_with_build_diagnostic(self):
        candidate = self.make_candidate()
        pyproject = candidate / "pyproject.toml"
        pyproject.write_text(
            pyproject.read_text(encoding="utf-8").replace(
                "setuptools.build_meta", "missing_backend"
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_checker(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("wheel build failed", result.stdout + result.stderr)

    def test_installed_help_mismatch_fails_with_diagnostic(self):
        candidate = self.make_candidate()
        entry = candidate / "writwall_cli" / "__main__.py"
        entry.write_text(
            entry.read_text(encoding="utf-8").replace(
                "Start with an idea", "Begin elsewhere"
            ),
            encoding="utf-8",
            newline="\n",
        )
        start = candidate / "scripts" / "start_writwall.py"
        start.write_text(
            start.read_text(encoding="utf-8").replace(
                "Start with an idea", "Begin elsewhere"
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_checker(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("installed help omitted", result.stdout + result.stderr)

    def test_missing_promised_handoff_fails_with_diagnostic(self):
        candidate = self.make_candidate()
        start = candidate / "scripts" / "start_writwall.py"
        start.write_text(
            start.read_text(encoding="utf-8").replace(
                'OUTPUT_NAME = ".writwall-bootstrap"',
                'OUTPUT_NAME = ".wrong-bootstrap"',
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_checker(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("complete handoff failed", result.stdout + result.stderr)

    def test_version_mismatch_is_rejected(self):
        checker = load_checker()
        with self.assertRaisesRegex(checker.ReleaseCheckError, "does not match"):
            checker.verify_installed_version("9.9.9", "0.9.0")

    def test_candidate_mutation_is_rejected(self):
        checker = load_checker()
        candidate = self.make_candidate()
        before = checker.tree_digest(candidate)
        (candidate / "pyproject.toml").write_text(
            "changed after baseline\n", encoding="utf-8", newline="\n"
        )
        with self.assertRaisesRegex(checker.ReleaseCheckError, "candidate changed"):
            checker.verify_candidate_unchanged(candidate, before)

    def test_release_identity_and_public_payload_are_coherent(self):
        with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
            project = tomllib.load(handle)["project"]
        self.assertEqual(project["version"], "0.9.0")
        publication = (REPO_ROOT / "PUBLICATION.md").read_text(encoding="utf-8")
        start = (REPO_ROOT / "START-HERE.md").read_text(encoding="utf-8")
        self.assertIn("v0.9.0", publication)
        self.assertIn("v0.9.0", start)
        self.assertIn("archive/refs/heads/main.zip", start)
        public_files = PUBLIC_FILES.read_text(encoding="utf-8").splitlines()
        self.assertIn("checks/check_coordinator_release.py", public_files)
        self.assertIn("tests/test_coordinator_release.py", public_files)


if __name__ == "__main__":
    unittest.main()
