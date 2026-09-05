# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Public-interface tests for the coordinator release-candidate gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
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
    from scripts.build_public_projection import complete_tree_ledger
    return complete_tree_ledger(root)


class CoordinatorReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.temp, True)

    def run_checker(self, candidate: Path, *extra: str):
        arguments = [str(candidate), *extra]
        if "--expected-tag" not in extra:
            arguments.extend(("--expected-tag", "v0.11.0"))
        return subprocess.run(
            [sys.executable, "-B", str(CHECKER), *arguments],
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

    def test_release_check_requires_an_intended_tag(self):
        candidate = self.make_candidate()
        result = subprocess.run(
            [sys.executable, "-B", str(CHECKER), str(candidate)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--expected-tag", result.stdout + result.stderr)
        self.assertIn("required", result.stdout + result.stderr)

    def test_published_release_metadata_accepts_matching_immutable_release(self):
        checker = load_checker()
        metadata = self.temp / "release.json"
        metadata.write_text(
            json.dumps({"tag_name": "v0.10.0", "immutable": True}),
            encoding="utf-8",
        )
        checker.verify_published_release_json(metadata, "v0.10.0")

    def test_published_release_metadata_rejects_nonimmutable_mismatch_and_malformed(self):
        checker = load_checker()
        cases = (
            ({"tag_name": "v0.10.0", "immutable": False}, "not immutable"),
            ({"tag_name": "v0.9.3", "immutable": True}, "does not match"),
            ({"tag_name": "v0.10.0", "immutable": "true"}, "literal true"),
            ({"immutable": True}, "tag_name"),
        )
        for index, (payload, diagnostic) in enumerate(cases):
            with self.subTest(payload=payload):
                metadata = self.temp / f"release-{index}.json"
                metadata.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaisesRegex(checker.ReleaseCheckError, diagnostic):
                    checker.verify_published_release_json(metadata, "v0.10.0")

        malformed = self.temp / "malformed.json"
        malformed.write_text('{"tag_name":', encoding="utf-8")
        with self.assertRaisesRegex(checker.ReleaseCheckError, "malformed JSON"):
            checker.verify_published_release_json(malformed, "v0.10.0")

    def test_published_release_metadata_rejects_duplicate_security_fields(self):
        checker = load_checker()
        metadata = self.temp / "duplicate.json"
        metadata.write_text(
            '{"tag_name":"v0.10.0","immutable":true,"immutable":false}',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(checker.ReleaseCheckError, "duplicate field"):
            checker.verify_published_release_json(metadata, "v0.10.0")

    def test_published_release_metadata_rejects_oversized_input(self):
        checker = load_checker()
        metadata = self.temp / "oversized.json"
        metadata.write_bytes(b" " * (checker.MAX_RELEASE_METADATA_BYTES + 1))
        with self.assertRaisesRegex(checker.ReleaseCheckError, "size limit"):
            checker.verify_published_release_json(metadata, "v0.10.0")

    def test_published_release_metadata_rejects_nonregular_input(self):
        checker = load_checker()
        with self.assertRaisesRegex(checker.ReleaseCheckError, "regular file"):
            checker.verify_published_release_json(self.temp, "v0.10.0")

    def test_complete_external_candidate_installs_and_emits_full_handoff(self):
        candidate = self.make_candidate()
        before = tree_digest(candidate)
        result = self.run_checker(candidate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK: coordinator release candidate passed", result.stdout)
        self.assertIn("installed command", result.stdout)
        self.assertIn("complete handoff", result.stdout)
        self.assertIn("adopted lockout", result.stdout)
        self.assertIn("retired lockout", result.stdout)
        self.assertIn("draft regression", result.stdout)
        self.assertIn("unrelated regression", result.stdout)
        self.assertIn("zero target-byte change", result.stdout)
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

    def test_installed_adopted_lockout_target_write_fails_release_gate(self):
        candidate = self.make_candidate()
        start = candidate / "scripts" / "start_writwall.py"
        start.write_text(
            start.read_text(encoding="utf-8").replace(
                "            emit_lifecycle_handoff(state)\n            return 0\n",
                "            emit_lifecycle_handoff(state)\n"
                "            (project / 'forbidden-route-write.txt').write_text('changed')\n"
                "            return 0\n",
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_checker(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "installed adopted-lockout route changed target bytes",
            result.stdout + result.stderr,
        )

    def test_installed_reintroduced_filename_only_adoption_defect_fails_release_gate(self):
        candidate = self.make_candidate()
        start = candidate / "scripts" / "start_writwall.py"
        original = start.read_text(encoding="utf-8")
        self.assertIn("adopted = bool(ratified_evidence)", original)
        start.write_text(
            original.replace(
                "adopted = bool(ratified_evidence)",
                "adopted = bool(adoption_evidence)",
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_checker(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "installed draft-adoption-record regression route failed",
            result.stdout + result.stderr,
        )

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

    def test_installed_missing_inspect_route_fails_with_diagnostic(self):
        candidate = self.make_candidate()
        entry = candidate / "writwall_cli" / "__main__.py"
        original = entry.read_text(encoding="utf-8")
        self.assertIn('if arguments[0] == "inspect":', original)
        entry.write_text(
            original.replace(
                'if arguments[0] == "inspect":',
                'if arguments[0] == "inspection":',
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_checker(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("installed inspect route", result.stdout + result.stderr)

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

    def test_release_gate_requires_bootstrap_addendum(self):
        checker = load_checker()
        self.assertIn(
            "writwall-adopt/assets/bootstrap-charter-addendum.md",
            checker.REQUIRED_HANDOFF_PATHS,
        )

    def test_wheel_data_files_include_bootstrap_addendum(self):
        with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
            project = tomllib.load(handle)
        data_files = project["tool"]["setuptools"]["data-files"]
        packaged = {
            path
            for paths in data_files.values()
            for path in paths
        }
        self.assertIn(
            "skills/writwall-adopt/assets/bootstrap-charter-addendum.md",
            packaged,
        )

    def test_omitted_packaged_bootstrap_addendum_fails_release_gate(self):
        candidate = self.make_candidate()
        pyproject = candidate / "pyproject.toml"
        pyproject.write_text(
            pyproject.read_text(encoding="utf-8").replace(
                '  "skills/writwall-adopt/assets/bootstrap-charter-addendum.md",\n',
                "",
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_checker(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("complete handoff failed", result.stdout + result.stderr)
        self.assertIn(
            "bootstrap-charter-addendum.md",
            result.stdout + result.stderr,
        )

    def test_emitted_bytecode_residue_fails_with_diagnostic(self):
        candidate = self.make_candidate()
        start = candidate / "scripts" / "start_writwall.py"
        start.write_text(
            start.read_text(encoding="utf-8").replace(
                "        _atomic_publish(stage, output)\n",
                "        _atomic_publish(stage, output)\n"
                "        residue = output / 'writwall-adopt' / 'assets' / "
                "'scripts' / '__pycache__' / 'planted.pyc'\n"
                "        residue.parent.mkdir(parents=True, exist_ok=True)\n"
                "        residue.write_bytes(b'planted regression residue')\n",
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_checker(candidate)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("bytecode residue", result.stdout + result.stderr)

    def test_version_mismatch_is_rejected(self):
        checker = load_checker()
        with self.assertRaisesRegex(checker.ReleaseCheckError, "does not match"):
            checker.verify_installed_version("9.9.9", "0.9.0")

    def test_intended_release_tag_must_match_candidate_metadata(self):
        candidate = self.make_candidate()
        pyproject = candidate / "pyproject.toml"
        pyproject.write_text(
            pyproject.read_text(encoding="utf-8").replace(
                'version = "0.11.0"', 'version = "0.9.0"'
            ),
            encoding="utf-8",
            newline="\n",
        )
        result = self.run_checker(candidate, "--expected-tag", "v0.11.0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "candidate version '0.9.0' does not match intended tag 'v0.11.0'",
            result.stdout + result.stderr,
        )

    def test_intended_release_tag_must_be_canonical_semver(self):
        candidate = self.make_candidate()
        result = self.run_checker(candidate, "--expected-tag", "v0.9.0-extra")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical vMAJOR.MINOR.PATCH", result.stdout + result.stderr)

    def test_intended_release_tag_rejects_non_ascii_digits(self):
        candidate = self.make_candidate()
        for tag in ("v1\u0661.2.3", "v1.2\u0662.3", "v1.2.3\u0663"):
            with self.subTest(tag=tag):
                result = self.run_checker(candidate, "--expected-tag", tag)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "canonical vMAJOR.MINOR.PATCH",
                    result.stdout + result.stderr,
                )

    def test_candidate_mutation_is_rejected(self):
        checker = load_checker()
        candidate = self.make_candidate()
        before = checker.tree_digest(candidate)
        (candidate / "pyproject.toml").write_text(
            "changed after baseline\n", encoding="utf-8", newline="\n"
        )
        with self.assertRaisesRegex(checker.ReleaseCheckError, "candidate changed"):
            checker.verify_candidate_unchanged(candidate, before)

    def test_release_check_reports_installed_canonical_root_evidence(self):
        candidate = self.make_candidate()
        result = self.run_checker(candidate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("canonical root", result.stdout.lower())

    def test_release_check_exercises_nested_worktree_stop_on_the_installed_wheel(self):
        candidate = self.make_candidate()
        result = self.run_checker(candidate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("worktree", result.stdout.lower())

    def test_release_identity_and_public_payload_are_coherent(self):
        with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
            project = tomllib.load(handle)["project"]
        self.assertEqual(project["version"], "0.11.0")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        adopting = (REPO_ROOT / "ADOPTING.md").read_text(encoding="utf-8")
        contributing = (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        publication = (REPO_ROOT / "PUBLICATION.md").read_text(encoding="utf-8")
        start = (REPO_ROOT / "START-HERE.md").read_text(encoding="utf-8")
        tagged_archive = "archive/refs/tags/v0.11.0.zip"
        self.assertIn(tagged_archive, readme)
        self.assertIn(tagged_archive, adopting)
        self.assertIn(tagged_archive, start)
        self.assertIn("--expected-tag v0.11.0", publication)
        self.assertIn("--expected-tag v0.11.0", contributing)
        for document in (readme, adopting, start):
            self.assertNotIn("not yet published", document)
            self.assertIn(
                'python -m pip install '
                '"https://github.com/HLLMR/writwall/archive/refs/tags/v0.11.0.zip"',
                document,
            )
            self.assertIn("writwall inspect", document)
            self.assertNotIn("does **not** contain `writwall inspect`", document)
        self.assertIn("Release `v0.9.0` first introduced", start)
        self.assertIn("Release `v0.9.1` corrected", start)
        self.assertIn("Release `v0.9.2` corrects", start)
        self.assertIn("Release `v0.9.3` adds", start)
        public_files = PUBLIC_FILES.read_text(encoding="utf-8").splitlines()
        self.assertIn("checks/check_coordinator_release.py", public_files)
        self.assertIn("tests/test_coordinator_release.py", public_files)

    def test_public_entry_docs_share_one_canonical_onboarding_lifecycle(self):
        documents = {
            name: (REPO_ROOT / name).read_text(encoding="utf-8")
            for name in (
                "README.md",
                "START-HERE.md",
                "ADOPTING.md",
                "docs/day-zero-coordinator.md",
                "docs/architect-interview.md",
            )
        }
        for name, document in documents.items():
            with self.subTest(document=name):
                self.assertIn("one canonical lifecycle", document)
                self.assertIn("writwall start --project-root", document)
                self.assertIn("writwall inspect --project-root", document)
                self.assertIn("fresh Architect", document)
                self.assertIn("fresh General", document)
                self.assertNotIn("## 2. Route A", document)
                self.assertNotIn("## 3. Route B", document)
                self.assertNotIn("## 4. Route C", document)

        workplace = documents["README.md"] + documents["START-HERE.md"]
        self.assertIn("Using Writwall at work", workplace)
        self.assertIn("employer-approved", workplace)
        self.assertIn("does not launch", workplace)
        self.assertIn("Act as the Writwall Architect", workplace)
        self.assertIn("Act as a fresh Writwall General", workplace)

        for name in (
            "START-HERE.md",
            "ADOPTING.md",
            "docs/day-zero-coordinator.md",
        ):
            rows = [
                line for line in documents[name].splitlines()
                if line.lstrip().startswith("|") and "--structured-intake" in line
            ]
            self.assertTrue(rows, name)
            for row in rows:
                self.assertIn("Architect", row, name)
                self.assertNotIn("Adoption coordinator", row, name)

    # -- WO-WW-021: the installed-wheel release gate confirms the new
    # Owner/Architect/General/Operator topology reaches the installed
    # coordinator, including the adopted-lockout route now naming a fresh
    # General rather than the old "Owner-Agent / Project-Architect" text.
    # Added RED in this work order; now exercised against the GREEN
    # implementation.

    def test_installed_release_gate_confirms_general_role_for_adopted_lockout(self):
        candidate = self.make_candidate()
        result = self.run_checker(candidate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("General", result.stdout)

    def test_installed_release_gate_exercises_conversation_first_clean_project(self):
        candidate = self.make_candidate()
        result = self.run_checker(candidate)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("conversation-first", result.stdout)


if __name__ == "__main__":
    unittest.main()
