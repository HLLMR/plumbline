# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Tests for the scaffolder (init.sh), Doctrine 6.4.1 step 8 support.

Skipped when bash is unavailable; the untested platform is then stated in the
remediation report. Every test writes exclusively inside its own temporary
fixture directory.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INIT_SH = REPO_ROOT / "init.sh"


def _is_wsl_launcher(bash_path: str | None) -> bool:
    """True when `bash_path` is Windows' System32\\bash.exe WSL launcher.

    That launcher runs inside a WSL distro's own filesystem namespace. On a
    distro with no drvfs mount for this machine's drives, it can never reach
    a Windows path at all, so it is not a usable bash for these tests, not
    merely one that needs a different path spelling.
    """
    if not bash_path:
        return False
    parts = [p.lower() for p in Path(bash_path).parts]
    return Path(bash_path).name.lower() == "bash.exe" and "system32" in parts


def _discover_bash() -> str | None:
    """Prefer a native Git Bash over the Windows WSL launcher.

    On Windows, `shutil.which("bash")` can resolve to the WSL launcher ahead
    of an installed Git Bash on PATH. Both accept ordinary POSIX-style paths
    to a Windows filesystem location, so once a native bash is selected, no
    further path translation is needed. Prefer Git Bash's two common install
    locations first; fall back to `shutil.which` only if neither exists, and
    then only if that result is not the unmounted WSL launcher, which is
    treated as bash being unavailable rather than run and failed.
    """
    if sys.platform != "win32":
        return shutil.which("bash")
    for candidate in (
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
    ):
        if Path(candidate).is_file():
            return candidate
    found = shutil.which("bash")
    if _is_wsl_launcher(found):
        return None
    return found


BASH = _discover_bash()

# On Windows, a direct (non-login) invocation of Git Bash inherits the
# Windows process PATH, which lacks /usr/bin, so core utilities like
# `dirname` and `mkdir` are missing. `-l` makes it a login shell, which
# loads /usr/bin onto PATH. Native Unix bash needs no such flag and keeps
# running exactly as before.
BASH_CMD = [BASH, "-l"] if BASH is not None and sys.platform == "win32" else [BASH]


def _native_bash_temp_root() -> Path:
    """Create a fixture root in the selected shell's own addressable temp.

    On Windows this avoids assuming that Python's user-profile temporary
    directory is writable from a restricted Git Bash runner. The fixture is
    instead created as a unique, cleanup-managed directory under the already
    writable project workspace. The WSL launcher remains excluded.
    """
    if sys.platform != "win32":
        return Path(tempfile.mkdtemp()).resolve()
    return Path(tempfile.mkdtemp(prefix=".wo-pl-026-init-", dir=REPO_ROOT)).resolve()


@unittest.skipIf(BASH is None, "bash is not available on this platform")
class InitScriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = _native_bash_temp_root()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.target = self.tmp / "project"
        self.target.mkdir()

    def make_git_dir(self):
        (self.target / ".git").mkdir()

    def make_git_file(self):
        (self.target / ".git").write_text(
            "gitdir: ../.git/worktrees/wt\n", encoding="utf-8")

    def run_init(self, *args, expect_success=True):
        result = subprocess.run(
            [*BASH_CMD, INIT_SH.as_posix(), *args, self.target.as_posix()],
            capture_output=True, text=True, timeout=120)
        if expect_success:
            self.assertEqual(result.returncode, 0,
                             f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        return result

    def test_selected_bash_can_round_trip_its_native_temporary_root(self):
        root = _native_bash_temp_root()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        probe = subprocess.run(
            [*BASH_CMD, "-c", 'test -d "$1"', "bash", root.as_posix()],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(probe.returncode, 0,
                         f"stdout:\n{probe.stdout}\nstderr:\n{probe.stderr}")

    def test_refuses_non_git_directory(self):
        result = self.run_init(expect_success=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a git repository", result.stderr)
        self.assertFalse((self.target / "governance").exists())

    def test_refuses_missing_directory(self):
        result = subprocess.run(
            [*BASH_CMD, INIT_SH.as_posix(), (self.tmp / "nope").as_posix()],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 1)
        self.assertIn("not a directory", result.stderr)

    def test_requires_a_target(self):
        result = subprocess.run(
            [*BASH_CMD, INIT_SH.as_posix()],
            capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 2)
        self.assertIn("usage", result.stderr)

    def test_rejects_unknown_option(self):
        result = self.run_init("--wipe-everything", expect_success=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown option", result.stderr)

    def test_accepts_git_directory(self):
        self.make_git_dir()
        self.run_init()
        self.assertTrue((self.target / "governance" / "work-orders").is_dir())

    def test_accepts_git_file_worktree(self):
        self.make_git_file()
        result = self.run_init()
        self.assertTrue((self.target / "governance" / "work-orders").is_dir())
        self.assertIn("governance/work-orders/", result.stdout)

    def test_creates_expected_layout(self):
        self.make_git_dir()
        self.run_init()
        for name in ("decisions", "work-orders", "reports", "briefs", "rfis",
                     "history", "archive", "scratch", "templates"):
            self.assertTrue((self.target / "governance" / name).is_dir(), name)
        self.assertTrue((self.target / "governance" / "LOG.md").is_file())
        self.assertTrue((self.target / "governance" / "LOG-denials.jsonl").is_file())
        self.assertFalse((self.target / "governance" / "LOG-denials.txt").exists(),
                         "the retired raw denial log must not be scaffolded")
        for letter in "ABCDE":
            matches = list((self.target / "governance" / "templates").glob(f"{letter}-*.md"))
            self.assertEqual(len(matches), 1, letter)

    def test_makes_no_commit_and_no_adoption_record(self):
        self.make_git_dir()
        self.run_init()
        self.assertFalse((self.target / "governance" / "decisions" / "DR-001.md").exists())
        self.assertFalse((self.target / "governance" / "PLAN.md").exists())
        # No claim that a birth test ran.
        denials = (self.target / "governance" / "LOG-denials.jsonl").read_text(encoding="utf-8")
        self.assertEqual(denials, "")

    def test_final_message_prevents_instructionless_lockout(self):
        self.make_git_dir()
        result = self.run_init()
        self.assertIn("START-HERE.md", result.stdout)
        self.assertIn("make the adoption bundle local before", result.stdout)
        self.assertIn("Do not register the wall yet", result.stdout)
        self.assertIn("already registered", result.stdout)
        self.assertIn("exact recorder authority", result.stdout)
        self.assertNotIn("needs a human", result.stdout)
        self.assertNotIn("by hand", result.stdout)

    def test_local_first_walkthrough_keeps_bundle_before_wall_registration(self):
        self.make_git_dir()
        bundle = self.target / ".claude" / "skills" / "writwall-adopt"
        shutil.copytree(REPO_ROOT / "skills" / "writwall-adopt", bundle)

        result = self.run_init()

        self.assertTrue((bundle / "SKILL.md").is_file())
        self.assertTrue((self.target / "governance").is_dir())
        self.assertTrue(
            (self.target / "checks" / "check_work_order_dispatch.py").is_file())
        self.assertTrue(
            (self.target / ".claude" / "hooks" /
             "wo_capability_wall.py").is_file())
        self.assertFalse((self.target / ".claude" / "settings.json").exists())
        self.assertFalse((self.target / ".claude" / "active-wo.txt").exists())
        self.assertIn("Do not register the wall yet", result.stdout)

    def test_second_run_is_create_only(self):
        self.make_git_dir()
        self.run_init()
        log = self.target / "governance" / "LOG.md"
        log.write_text("LOCAL CONTENT MUST SURVIVE\n", encoding="utf-8")
        template = self.target / "governance" / "templates" / "A-charter.md"
        template.write_text("LOCAL TEMPLATE EDIT\n", encoding="utf-8")

        result = self.run_init()
        self.assertEqual(log.read_text(encoding="utf-8"), "LOCAL CONTENT MUST SURVIVE\n")
        self.assertEqual(template.read_text(encoding="utf-8"), "LOCAL TEMPLATE EDIT\n")
        self.assertIn("governance/LOG.md", result.stdout)
        self.assertIn("skipped", result.stdout)

    def test_never_copies_writwall_working_records(self):
        """Doctrine 5.1.5: the scaffolder is an adoption route and must carry
        none of Writwall's own governance records into the target."""
        self.make_git_dir()
        (self.target / ".claude").mkdir()
        self.run_init()
        for name in ("CLAUDE.md", "SELF-HOSTING.md", "DOCTRINE.md", "README.md",
                     "ADOPTING.md", "REMEDIATION-REPORT.md"):
            self.assertFalse((self.target / name).exists(),
                             f"{name} was copied into the target project")
        for name in ("decisions", "bootstrap", "archive", "scripts",
                     "skills", "migration-guides", "tests"):
            self.assertFalse((self.target / name).exists(),
                             f"{name}/ was copied into the target project")
        # What it does install is exactly the project-side footprint.
        self.assertTrue((self.target / "governance").is_dir())
        self.assertTrue((self.target / ".claude" / "hooks" /
                         "wo_capability_wall.py").is_file())
        # checks/ carries only the adopter-facing dispatch validator, never
        # Writwall's own internal check scripts (e.g. check_distribution.py).
        checks_contents = sorted(p.name for p in (self.target / "checks").iterdir())
        self.assertEqual(checks_contents, ["check_work_order_dispatch.py"])

    def test_installed_governance_archive_is_the_targets_own(self):
        """governance/archive/ belongs to the adopting project and must not be
        seeded with Writwall's historical material."""
        self.make_git_dir()
        self.run_init()
        archive = self.target / "governance" / "archive"
        self.assertTrue(archive.is_dir())
        contents = [p.name for p in archive.iterdir() if p.name != ".gitkeep"]
        self.assertEqual(contents, [])

    def test_refuses_existing_charter(self):
        self.make_git_dir()
        (self.target / "CLAUDE.md").write_text("# existing charter\n", encoding="utf-8")
        result = self.run_init()
        self.assertIn("CLAUDE.md", result.stdout)
        self.assertIn("refused", result.stdout)
        self.assertEqual((self.target / "CLAUDE.md").read_text(encoding="utf-8"),
                         "# existing charter\n")

    def test_refuses_existing_hook_registration(self):
        self.make_git_dir()
        (self.target / ".claude").mkdir()
        settings = self.target / ".claude" / "settings.json"
        settings.write_text('{"hooks": {"PreToolUse": []}}', encoding="utf-8")
        result = self.run_init()
        self.assertEqual(settings.read_text(encoding="utf-8"),
                         '{"hooks": {"PreToolUse": []}}')
        self.assertIn(".claude/settings.json", result.stdout)

    def test_installs_adapter_when_claude_dir_exists(self):
        self.make_git_dir()
        (self.target / ".claude").mkdir()
        self.run_init()
        installed = self.target / ".claude" / "hooks" / "wo_capability_wall.py"
        self.assertTrue(installed.is_file())
        self.assertEqual(
            installed.read_bytes(),
            (REPO_ROOT / "adapters" / "claude-code" / "wo_capability_wall.py").read_bytes())

    def test_does_not_overwrite_existing_adapter_without_force(self):
        self.make_git_dir()
        hooks = self.target / ".claude" / "hooks"
        hooks.mkdir(parents=True)
        installed = hooks / "wo_capability_wall.py"
        installed.write_text("# locally modified adapter\n", encoding="utf-8")
        self.run_init()
        self.assertEqual(installed.read_text(encoding="utf-8"),
                         "# locally modified adapter\n")

    def test_force_adapter_overwrites_only_the_adapter(self):
        self.make_git_dir()
        hooks = self.target / ".claude" / "hooks"
        hooks.mkdir(parents=True)
        installed = hooks / "wo_capability_wall.py"
        installed.write_text("# locally modified adapter\n", encoding="utf-8")
        self.run_init()
        log = self.target / "governance" / "LOG.md"
        log.write_text("LOCAL CONTENT MUST SURVIVE\n", encoding="utf-8")

        self.run_init("--force-adapter")
        self.assertEqual(
            installed.read_bytes(),
            (REPO_ROOT / "adapters" / "claude-code" / "wo_capability_wall.py").read_bytes())
        self.assertEqual(log.read_text(encoding="utf-8"), "LOCAL CONTENT MUST SURVIVE\n")

    def test_installs_checker_create_only(self):
        self.make_git_dir()
        result = self.run_init()
        installed = self.target / "checks" / "check_work_order_dispatch.py"
        self.assertTrue(installed.is_file())
        self.assertEqual(
            installed.read_bytes(),
            (REPO_ROOT / "checks" / "check_work_order_dispatch.py").read_bytes())
        self.assertIn("checks/check_work_order_dispatch.py", result.stdout)

    def test_does_not_overwrite_existing_checker(self):
        self.make_git_dir()
        checks_dir = self.target / "checks"
        checks_dir.mkdir()
        installed = checks_dir / "check_work_order_dispatch.py"
        installed.write_text("# locally modified checker\n", encoding="utf-8")
        result = self.run_init()
        self.assertEqual(installed.read_text(encoding="utf-8"),
                         "# locally modified checker\n")
        self.assertIn("checks/check_work_order_dispatch.py", result.stdout)
        self.assertIn("skipped", result.stdout)

    def test_scaffolder_and_bundle_routes_agree_on_b_template_and_migration_guide(self):
        """Route-consistency lock for Doctrine 0.7 (DR-004): the scaffolder
        route installs the current canonical B-work-order template
        byte-for-byte, with exactly one enforced_by: {} default and exactly
        one generated-boundary marker pair; the adoption-bundle route's own
        B template copy is byte-identical to the same canonical source; the
        canonical and bundled 0.6-to-0.7 migration guides exist and match;
        and the scaffolder does not begin copying migration guides into the
        target (Doctrine 5.1.5 footprint rule, unchanged by this migration)."""
        self.make_git_dir()
        self.run_init()

        canonical_b = (REPO_ROOT / "templates" / "B-work-order.md").read_bytes()
        installed_b = (self.target / "governance" / "templates" /
                       "B-work-order.md").read_bytes()
        self.assertEqual(installed_b, canonical_b)
        self.assertIn(b"enforced_by: {}", canonical_b)
        self.assertEqual(canonical_b.count(b"<!-- BEGIN GENERATED BOUNDARIES -->"), 1)
        self.assertEqual(canonical_b.count(b"<!-- END GENERATED BOUNDARIES -->"), 1)

        bundled_b = (REPO_ROOT / "skills" / "writwall-adopt" / "assets" /
                    "templates" / "B-work-order.md").read_bytes()
        self.assertEqual(bundled_b, canonical_b)

        canonical_guide = REPO_ROOT / "migration-guides" / "0.6-to-0.7.md"
        bundled_guide = (REPO_ROOT / "skills" / "writwall-adopt" / "references" /
                         "migration-guides" / "0.6-to-0.7.md")
        self.assertTrue(canonical_guide.is_file())
        self.assertTrue(bundled_guide.is_file())
        self.assertEqual(bundled_guide.read_bytes(), canonical_guide.read_bytes())

        self.assertFalse(
            (self.target / "migration-guides").exists(),
            "init.sh must not copy Writwall migration guides into the "
            "target project (Doctrine 5.1.5)")

    def test_force_templates_overwrites_only_templates(self):
        self.make_git_dir()
        self.run_init()
        template = self.target / "governance" / "templates" / "A-charter.md"
        template.write_text("LOCAL TEMPLATE EDIT\n", encoding="utf-8")
        log = self.target / "governance" / "LOG.md"
        log.write_text("LOCAL CONTENT MUST SURVIVE\n", encoding="utf-8")

        self.run_init("--force-templates")
        self.assertEqual(
            template.read_bytes(),
            (REPO_ROOT / "templates" / "A-charter.md").read_bytes())
        self.assertEqual(log.read_text(encoding="utf-8"), "LOCAL CONTENT MUST SURVIVE\n")


if __name__ == "__main__":
    unittest.main()
