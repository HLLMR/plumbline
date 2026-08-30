# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Public-interface tests for Writwall's managed local privacy screen."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import privacy_screen


REPO_ROOT = Path(__file__).resolve().parents[1]


class PrivacyScreenTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.temp = Path(self.temp_dir.name).resolve()
        self.project = self.temp / "project"
        self.project.mkdir()
        self.state = self.temp / "state"

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["WRITWALL_STATE_HOME"] = str(self.state)
        return subprocess.run(
            [sys.executable, "-B", "-m", "writwall_cli", *arguments],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_privacy_init_creates_a_non_disclosing_project_profile(self) -> None:
        result = self.run_cli(
            "privacy", "init", "--project-root", str(self.project)
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertRegex(result.stdout, r"privacy screen: ready \([1-9][0-9]* entries\)")
        self.assertNotIn(str(self.project), result.stdout + result.stderr)
        self.assertNotIn(str(self.state), result.stdout + result.stderr)
        profiles = list(self.state.rglob("private-patterns.txt"))
        self.assertEqual(len(profiles), 1)
        self.assertIn(str(self.project), profiles[0].read_text(encoding="utf-8"))

    def test_privacy_add_and_status_report_counts_without_disclosure(self) -> None:
        initialized = self.run_cli(
            "privacy", "init", "--project-root", str(self.project)
        )
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        initial_count = int(initialized.stdout.split("(", 1)[1].split()[0])
        private_identifier = "CLIENT-CODENAME-ORCHARD"

        refused = self.run_cli(
            "privacy", "add", "--project-root", str(self.project),
            "--identifier-stdin",
        )
        self.assertNotEqual(refused.returncode, 0)

        environment = self.managed_environment()
        added = subprocess.run(
            [sys.executable, "-B", "-m", "writwall_cli", "privacy", "add",
             "--project-root", str(self.project), "--identifier-stdin",
             "--confirm-no-secrets"],
            cwd=REPO_ROOT, env=environment, input=private_identifier + "\n",
            capture_output=True, text=True, timeout=30,
        )
        status = self.run_cli(
            "privacy", "status", "--project-root", str(self.project)
        )

        self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
        self.assertEqual(status.returncode, 0, status.stdout + status.stderr)
        self.assertIn(f"{initial_count + 1} entries", added.stdout)
        self.assertIn(f"{initial_count + 1} entries", status.stdout)
        combined = added.stdout + added.stderr + status.stdout + status.stderr
        self.assertNotIn(private_identifier, combined)
        self.assertNotIn(str(self.state), combined)

    def managed_environment(self) -> dict[str, str]:
        environment = os.environ.copy()
        environment["WRITWALL_STATE_HOME"] = str(self.state)
        return environment

    def test_profile_locations_are_platform_native_and_project_specific(self) -> None:
        other = self.temp / "other-project"
        other.mkdir()
        windows_env = {"LOCALAPPDATA": str(self.temp / "LocalAppData")}
        linux_env = {"XDG_STATE_HOME": str(self.temp / "xdg")}

        windows = privacy_screen.profile_path(
            self.project, platform="win32", environment=windows_env
        )
        linux = privacy_screen.profile_path(
            self.project, platform="linux", environment=linux_env
        )
        mac = privacy_screen.profile_path(
            self.project, platform="darwin", environment={}, home=self.temp / "home"
        )
        second = privacy_screen.profile_path(
            other, platform="linux", environment=linux_env
        )

        self.assertEqual(windows.parts[-4:-2], ("Writwall", "projects"))
        self.assertEqual(linux.parts[-4:-2], ("writwall", "projects"))
        self.assertEqual(mac.parts[-6:-2], (".local", "state", "writwall", "projects"))
        self.assertNotEqual(linux.parent.name, second.parent.name)

    def test_state_override_inside_project_is_rejected_before_write(self) -> None:
        unsafe_state = self.project / ".private-state"
        environment = os.environ.copy()
        environment["WRITWALL_STATE_HOME"] = str(unsafe_state)

        result = subprocess.run(
            [sys.executable, "-B", "-m", "writwall_cli", "privacy", "init",
             "--project-root", str(self.project)],
            cwd=REPO_ROOT, env=environment, capture_output=True, text=True,
            timeout=30,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(unsafe_state.exists())
        self.assertNotIn(str(unsafe_state), result.stdout + result.stderr)

    def test_profile_symlink_is_rejected_without_touching_its_target(self) -> None:
        environment = {"WRITWALL_STATE_HOME": str(self.state)}
        profile = privacy_screen.profile_path(
            self.project, environment=environment
        )
        profile.parent.mkdir(parents=True)
        outside = self.temp / "outside.txt"
        outside.write_text("unchanged\n", encoding="utf-8")
        try:
            profile.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"symlink unavailable: {exc}")
        process_environment = os.environ.copy()
        process_environment.update(environment)

        result = subprocess.run(
            [sys.executable, "-B", "-m", "writwall_cli", "privacy", "init",
             "--project-root", str(self.project)],
            cwd=REPO_ROOT, env=process_environment, capture_output=True,
            text=True, timeout=30,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(outside.read_text(encoding="utf-8"), "unchanged\n")
        self.assertNotIn(str(outside), result.stdout + result.stderr)

    def test_profile_ancestor_symlink_is_rejected_before_write(self) -> None:
        environment = {"WRITWALL_STATE_HOME": str(self.state)}
        profile = privacy_screen.profile_path(self.project, environment=environment)
        projects = profile.parent.parent
        projects.mkdir(parents=True)
        redirected = self.temp / "redirected"
        redirected.mkdir()
        try:
            profile.parent.symlink_to(redirected, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlink unavailable: {exc}")
        process_environment = os.environ.copy()
        process_environment.update(environment)

        result = subprocess.run(
            [sys.executable, "-B", "-m", "writwall_cli", "privacy", "init",
             "--project-root", str(self.project)],
            cwd=REPO_ROOT, env=process_environment, capture_output=True,
            text=True, timeout=30,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((redirected / "private-patterns.txt").exists())

    def test_obvious_credential_shaped_identifier_is_rejected(self) -> None:
        initialized = self.run_cli(
            "privacy", "init", "--project-root", str(self.project)
        )
        self.assertEqual(initialized.returncode, 0, initialized.stderr)

        result = subprocess.run(
            [sys.executable, "-B", "-m", "writwall_cli", "privacy", "add",
             "--project-root", str(self.project), "--identifier-stdin",
             "--confirm-no-secrets"],
            cwd=REPO_ROOT, env=self.managed_environment(),
            input="password=synthetic-not-a-secret\n", capture_output=True,
            text=True, timeout=30,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("synthetic-not-a-secret", result.stdout + result.stderr)

    def test_concurrent_additions_are_serialized_without_lost_updates(self) -> None:
        initialized = self.run_cli(
            "privacy", "init", "--project-root", str(self.project)
        )
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        identifiers = [f"PRIVATE-PROJECT-MARKER-{number:02d}" for number in range(12)]
        processes: list[subprocess.Popen[str]] = []
        for identifier in identifiers:
            process = subprocess.Popen(
                [sys.executable, "-B", "-m", "writwall_cli", "privacy", "add",
                 "--project-root", str(self.project), "--identifier-stdin",
                 "--confirm-no-secrets"],
                cwd=REPO_ROOT, env=self.managed_environment(), stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            assert process.stdin is not None
            process.stdin.write(identifier + "\n")
            processes.append(process)
        for process in processes:
            assert process.stdin is not None
            process.stdin.close()
        results = []
        for process in processes:
            process.wait(timeout=30)
            assert process.stdout is not None and process.stderr is not None
            stdout = process.stdout.read()
            stderr = process.stderr.read()
            process.stdout.close()
            process.stderr.close()
            results.append((process.returncode, stdout, stderr))

        self.assertTrue(all(code == 0 for code, _, _ in results), results)
        profile = next(self.state.rglob("private-patterns.txt"))
        stored = profile.read_text(encoding="utf-8")
        for identifier in identifiers:
            self.assertIn(identifier, stored)


if __name__ == "__main__":
    unittest.main()
