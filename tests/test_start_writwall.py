# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Public-interface tests for the day-zero Writwall coordinator."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from scripts import start_writwall as starter_module


REPO_ROOT = Path(__file__).resolve().parents[1]
STARTER = REPO_ROOT / "scripts" / "start_writwall.py"


class StartWritwallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.temp, True)
        self.project = self.temp / "project"
        self.project.mkdir()

    def run_start(self, *extra: str, project: Path | None = None):
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(STARTER),
                "--non-interactive",
                "--project-root",
                str(project or self.project),
                "--project-name",
                "Example project",
                "--purpose",
                "Build a small, governed project.",
                "--agent",
                "Claude Code in VS Code",
                "--location",
                "local workstation",
                "--environment",
                "local repository with separately administered hosting",
                "--owner-time",
                "no",
                "--confirm-no-secrets",
                *extra,
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )

    @property
    def output(self) -> Path:
        return self.project / ".writwall-bootstrap"

    def intake(self) -> dict:
        return json.loads((self.output / "intake.json").read_text(encoding="utf-8"))

    def handoff(self) -> str:
        return (self.output / "HANDOFF.md").read_text(encoding="utf-8")

    def test_clean_project_creates_bundle_and_exact_handoff(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.intake()["observed_state"], "clean_new")
        self.assertTrue((self.output / "writwall-adopt" / "SKILL.md").is_file())
        handoff = self.handoff()
        flat = " ".join(handoff.split())
        self.assertIn("Act as my Writwall adoption coordinator", handoff)
        self.assertIn("does not install or adopt Writwall", flat)
        self.assertIn("Do not enter passwords, API tokens", handoff)

    def test_create_only_refuses_existing_output_without_overwrite(self):
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_text("unchanged", encoding="utf-8")
        result = self.run_start()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "unchanged")
        self.assertEqual(sorted(p.name for p in self.output.iterdir()), ["keep.txt"])

    def test_missing_secret_confirmation_fails_before_output(self):
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(STARTER),
                "--non-interactive",
                "--project-root",
                str(self.project),
                "--project-name",
                "Example",
                "--purpose",
                "Example",
                "--agent",
                "Codex",
                "--location",
                "desktop",
                "--environment",
                "local repository",
                "--owner-time",
                "no",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())
        self.assertIn("secrets", (result.stdout + result.stderr).lower())

    def test_active_pointer_routes_to_implementer_only_when_target_is_active(self):
        work_order = self.project / "governance" / "work-orders" / "WO-001.md"
        work_order.parent.mkdir(parents=True)
        work_order.write_text("---\nid: WO-001\nstatus: ACTIVE\n---\n# Work\n",
                              encoding="utf-8")
        pointer = self.project / ".claude" / "active-wo.txt"
        pointer.parent.mkdir(parents=True)
        pointer.write_text("governance/work-orders/WO-001.md\n", encoding="utf-8")
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.intake()["observed_state"], "active_work_order")
        self.assertIn("Act as Implementer for the active work order only", self.handoff())

    def test_pointer_plus_second_active_order_stops_as_inconsistent(self):
        orders = self.project / "governance" / "work-orders"
        orders.mkdir(parents=True)
        for name in ("WO-001.md", "WO-002.md"):
            (orders / name).write_text(
                f"---\nid: {name[:-3]}\nstatus: ACTIVE\n---\n",
                encoding="utf-8",
            )
        pointer = self.project / ".claude" / "active-wo.txt"
        pointer.parent.mkdir(parents=True)
        pointer.write_text("governance/work-orders/WO-001.md\n", encoding="utf-8")
        result = self.run_start()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())
        self.assertIn("only active", (result.stdout + result.stderr).lower())

    def test_missing_pointer_with_closed_history_never_emits_resume_prompt(self):
        closed = self.project / "governance" / "history" / "WO-001.md"
        closed.parent.mkdir(parents=True)
        closed.write_text("---\nid: WO-001\nstatus: CLOSED\n---\n", encoding="utf-8")
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (self.project / "governance" / name).write_text(f"# {name}\n", encoding="utf-8")
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.intake()["observed_state"], "retired_lockout")
        handoff = self.handoff()
        self.assertIn("Act as Dispatcher", handoff)
        self.assertNotIn("resume", handoff.lower())
        self.assertNotIn("Act as Implementer", handoff)

    def test_pointer_to_closed_order_is_inconsistent_and_creates_nothing(self):
        work_order = self.project / "governance" / "work-orders" / "WO-001.md"
        work_order.parent.mkdir(parents=True)
        work_order.write_text("---\nid: WO-001\nstatus: CLOSED\n---\n", encoding="utf-8")
        pointer = self.project / ".claude" / "active-wo.txt"
        pointer.parent.mkdir(parents=True)
        pointer.write_text("governance/work-orders/WO-001.md\n", encoding="utf-8")
        result = self.run_start()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())
        self.assertIn("inconsistent", (result.stdout + result.stderr).lower())

    def test_partial_bootstrap_routes_to_recovery_coordinator(self):
        settings = self.project / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text("{}\n", encoding="utf-8")
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.intake()["observed_state"], "partial_bootstrap")
        self.assertIn("recovery coordinator", self.handoff())

    def test_adopted_lockout_routes_to_dispatcher(self):
        governance = self.project / "governance"
        governance.mkdir()
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(f"# {name}\n", encoding="utf-8")
        decision = governance / "decisions" / "DR-001.md"
        decision.parent.mkdir()
        decision.write_text("# Adoption record\n", encoding="utf-8")
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.intake()["observed_state"], "adopted_lockout")
        self.assertIn("Act as Dispatcher", self.handoff())

    def test_owner_time_yes_defines_capture_and_no_records_not_reported(self):
        yes = self.run_start("--owner-time", "yes")
        self.assertEqual(yes.returncode, 0, yes.stdout + yes.stderr)
        handoff = self.handoff()
        flat = " ".join(handoff.split())
        self.assertIn("Owner active-minute capture: ENABLED", handoff)
        self.assertIn("Human reading, deciding, responding, authentication", flat)

        shutil.rmtree(self.output)
        no = self.run_start()
        self.assertEqual(no.returncode, 0, no.stdout + no.stderr)
        self.assertIn("Owner active minutes: NOT REPORTED", self.handoff())

    def test_external_operators_receive_separate_inert_packets(self):
        result = self.run_start(
            "--external-operator", "DNS authority migration",
            "--external-operator", "mail routing cutover",
            "--external-operator", "mailbox data migration",
            "--external-operator", "repository and website work",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        packets = sorted(p.name for p in (self.output / "operations").glob("*.md"))
        self.assertEqual(packets, [
            "dns-authority-migration.md",
            "mail-routing-cutover.md",
            "mailbox-data-migration.md",
            "repository-and-website-work.md",
        ])
        for path in (self.output / "operations").glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for heading in (
                "## Preconditions", "## Permitted actions", "## Prohibited actions",
                "## Verification", "## Rollback", "## Evidence to return",
                "## Credential boundary",
            ):
                self.assertIn(heading, text)
            self.assertIn("confers no authority", text)

    def test_dns_mail_scenario_is_split_without_real_values(self):
        result = self.run_start("--scenario", "dns-mail-migration")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        intake = self.intake()
        self.assertEqual(intake["external_operator_functions"], [
            "DNS provider selection",
            "DNS inventory and cutover",
            "mail routing cutover",
            "mailbox data migration",
            "repository and website work",
        ])
        combined = self.handoff() + "\n" + "\n".join(
            path.read_text(encoding="utf-8")
            for path in (self.output / "operations").glob("*.md")
        )
        self.assertNotIn("fastmail", combined.lower())
        self.assertNotIn("proton", combined.lower())
        self.assertNotIn("hllmr", combined.lower())
        self.assertIn("eight domains", combined.lower())
        self.assertIn("dns authority cutover", combined.lower())
        self.assertIn("historical mailbox data", combined.lower())
        self.assertLess(
            combined.lower().index("dns authority cutover"),
            combined.lower().index("change mail routing"),
        )

    def test_complete_bundle_is_byte_identical_to_source(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        source = REPO_ROOT / "skills" / "writwall-adopt"
        copied = self.output / "writwall-adopt"
        source_files = sorted(
            path.relative_to(source).as_posix()
            for path in source.rglob("*") if path.is_file()
        )
        copied_files = sorted(
            path.relative_to(copied).as_posix()
            for path in copied.rglob("*") if path.is_file()
        )
        self.assertEqual(copied_files, source_files)
        for relative in source_files:
            self.assertEqual((copied / relative).read_bytes(),
                             (source / relative).read_bytes(), relative)

    def test_role_split_recommends_minimum_and_bounded_external_functions(self):
        result = self.run_start(
            "--external-operator", "DNS administration",
            "--external-operator", "mail administration",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        handoff = self.handoff()
        self.assertIn("Recommended smallest credible role split", handoff)
        self.assertIn("one human Owner, one Owner-Agent coordinator", handoff)
        self.assertIn("2 separately bounded external function packet(s)", handoff)

    def test_windows_reserved_operator_name_is_made_portable(self):
        result = self.run_start("--external-operator", "CON")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.output / "operations" / "operator-con.md").is_file())

    def test_dangling_output_symlink_is_a_collision(self):
        missing = self.project / "missing-output-target"
        try:
            self.output.symlink_to(missing, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")
        result = self.run_start()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.output.is_symlink())
        self.assertFalse(missing.exists())

    def test_atomic_publication_failure_leaves_no_target_output_or_stage(self):
        args = SimpleNamespace(
            project_name="Example",
            purpose="Example purpose",
            agent="Codex",
            location="desktop",
            environment="local repository",
            owner_time="no",
            scenario=None,
        )
        state = starter_module.ObservedState(
            "clean_new", ("activation pointer is absent",)
        )
        stage_pattern = f".{self.project.name}-writwall-bootstrap-stage-*"
        with mock.patch.object(
            starter_module.os, "rename", side_effect=OSError("injected rename failure")
        ):
            with self.assertRaises(starter_module.CoordinatorError) as raised:
                starter_module.write_bootstrap(self.project, args, state, ())
        self.assertIn("before atomic publication", str(raised.exception))
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.project.parent.glob(stage_pattern)), [])

    def test_nested_history_symlink_stops_before_external_read(self):
        external = self.temp / "external-history"
        external.mkdir()
        (external / "WO-001.md").write_text(
            "---\nid: WO-001\nstatus: CLOSED\n---\nSECRET-SENTINEL\n",
            encoding="utf-8",
        )
        governance = self.project / "governance"
        governance.mkdir()
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(f"# {name}\n", encoding="utf-8")
        try:
            (governance / "history").symlink_to(external, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"symlink creation unavailable: {exc}")
        result = self.run_start()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())
        self.assertIn("symlink", (result.stdout + result.stderr).lower())
        self.assertNotIn("SECRET-SENTINEL", result.stdout + result.stderr)

    def test_junction_detection_fallback_is_exercised(self):
        ordinary = self.project / "ordinary"
        ordinary.mkdir()
        with mock.patch.object(
            starter_module.os.path, "isjunction", create=True, return_value=True
        ):
            self.assertTrue(starter_module._is_linklike(ordinary))

    def test_interactive_flow_offers_brief_and_time_capture_before_intake(self):
        brief = self.temp / "existing-brief.md"
        brief.write_text("Existing project thesis.\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable, "-B", str(STARTER),
                "--project-root", str(self.project),
                "--project-name", "Interactive project",
            ],
            cwd=REPO_ROOT,
            input=(
                "yes\n"  # Owner-time choice
                "yes\n"  # no-secret confirmation
                f"{brief}\n"
                "\n"  # default agent
                "\n"  # default location
                "\n"  # default environment
                "\n"  # no external functions
            ),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertLess(
            result.stdout.index("Track Owner active minutes"),
            result.stdout.index("Continue without entering secrets"),
        )
        self.assertIn("Existing project brief file path", result.stdout)
        self.assertEqual(self.intake()["purpose"], "Existing project thesis.")

    def test_brief_file_is_read_but_never_modified(self):
        brief = self.temp / "brief.md"
        brief.write_text("A supplied project thesis.\n", encoding="utf-8")
        result = self.run_start("--brief-file", str(brief))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(brief.read_text(encoding="utf-8"),
                         "A supplied project thesis.\n")
        self.assertEqual(self.intake()["purpose"], "A supplied project thesis.")

    def test_paths_are_recorded_portably(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = (self.output / "intake.json").read_text(encoding="utf-8")
        self.assertNotIn("\\", text)
        self.assertIn(".writwall-bootstrap", self.handoff())

    def test_environment_is_captured_without_becoming_authority(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            self.intake()["repository_external_environment"],
            "local repository with separately administered hosting",
        )
        self.assertIn(
            "Repository and external environment: local repository with separately administered hosting",
            self.handoff(),
        )
        self.assertEqual(self.intake()["authority"], "unratified_intake_only")


if __name__ == "__main__":
    unittest.main()
