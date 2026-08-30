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

    def run_idea_start(self, *extra: str, project: Path | None = None):
        return subprocess.run(
            [
                sys.executable, "-B", "-m", "writwall_cli", "start",
                "--non-interactive",
                "--project-root", str(project or self.project),
                "--problem", "Small teams lose decisions between idea and implementation.",
                "--intended-user", "A technical founder working with agents.",
                "--why-matters", "Early ambiguity causes expensive rework.",
                "--evidence", "Two abandoned prototypes; demand remains an assumption.",
                "--smallest-outcome", "A ratifiable discovery packet.",
                "--success-signal", "The Owner can approve or stop without reconstruction.",
                "--constraint", "Local-only and standard library.",
                "--non-goal", "No production deployment.",
                "--risk", "The workflow may be too heavy for small ideas.",
                "--kill-condition", "Stop if qualification cannot name a useful outcome.",
                "--asset", "An existing written brief.",
                "--agent", "Codex",
                "--location", "local workstation",
                "--environment", "local repository only",
                "--owner-time", "no",
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

    def install_writwall(self) -> Path:
        build_source = self.temp / "build-source"
        shutil.copytree(
            REPO_ROOT,
            build_source,
            ignore=shutil.ignore_patterns(
                ".git", "dist", "archive", "governance", "tests",
                "__pycache__", "*.egg-info",
            ),
        )
        wheelhouse = self.temp / "wheelhouse"
        wheelhouse.mkdir()
        build = subprocess.run(
            [
                sys.executable, "-m", "pip", "wheel", "--no-deps",
                "--no-build-isolation", "--wheel-dir", str(wheelhouse),
                str(build_source),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
        wheels = list(wheelhouse.glob("writwall-*.whl"))
        self.assertEqual(len(wheels), 1, build.stdout + build.stderr)

        venv = self.temp / "venv"
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv)],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        python = venv / ("Scripts/python.exe" if sys.platform == "win32"
                         else "bin/python")
        install = subprocess.run(
            [
                str(python), "-m", "pip", "install", "--no-deps",
                str(wheels[0]),
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        return venv / ("Scripts/writwall.exe" if sys.platform == "win32"
                       else "bin/writwall")

    def test_isolated_install_exposes_writwall_start(self):
        command = self.install_writwall()
        result = subprocess.run(
            [str(command), "start", "--help"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Start with an idea", result.stdout)

    def test_isolated_install_runs_the_real_coordinator(self):
        command = self.install_writwall()
        result = subprocess.run(
            [
                str(command), "start", "--non-interactive",
                "--project-root", str(self.project),
                "--project-name", "Example project",
                "--purpose", "Build a small, governed project.",
                "--agent", "Codex",
                "--location", "local workstation",
                "--environment", "local repository only",
                "--owner-time", "no",
                "--confirm-no-secrets",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.output / "HANDOFF.md").is_file())
        self.assertTrue((self.output / "writwall-adopt" / "SKILL.md").is_file())
        for relative in (
            "assets/scripts/collect_name_clearance.py",
            "assets/checks/check_name_clearance.py",
            "references/name-clearance.md",
        ):
            self.assertTrue((self.output / "writwall-adopt" / relative).is_file(), relative)

    def test_unnamed_idea_emits_complete_unratified_architect_packet_set(self):
        result = self.run_idea_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        discovery = json.loads(
            (self.output / "discovery.json").read_text(encoding="utf-8")
        )
        self.assertEqual(discovery["identity"]["state"], "unnamed")
        self.assertEqual(discovery["authority"], "unratified_discovery_only")
        for field in (
            "problem_or_opportunity", "intended_user", "why_outcome_matters",
            "evidence_and_assumptions", "smallest_useful_outcome", "success_signal",
            "constraints", "non_goals", "material_risks", "stop_kill_conditions",
            "existing_assets", "repository_runtime_deployment_environment",
            "preferred_agent_interface", "external_systems_and_operators",
            "owner_time_capture",
        ):
            self.assertIn(field, discovery["qualification"])
        for relative in (
            "OWNER-AGENT.md", "REPOSITORY-OPERATOR.md", "REVIEWER.md",
            "NAME-CLEARANCE.md", "OWNER-RATIFICATION.md",
        ):
            text = (self.output / relative).read_text(encoding="utf-8")
            self.assertIn("unratified", text.lower(), relative)

    def test_observed_boundaries_select_different_smallest_credible_topologies(self):
        local = self.run_idea_start()
        self.assertEqual(local.returncode, 0, local.stdout + local.stderr)
        local_discovery = json.loads(
            (self.output / "discovery.json").read_text(encoding="utf-8")
        )
        self.assertEqual(local_discovery["topology"]["tier"], "local_only")

        high_impact_project = self.temp / "high-impact-project"
        high_impact_project.mkdir()
        high_impact = self.run_idea_start(
            "--scenario", "dns-mail-migration", project=high_impact_project
        )
        self.assertEqual(
            high_impact.returncode, 0, high_impact.stdout + high_impact.stderr
        )
        high_output = high_impact_project / ".writwall-bootstrap"
        high_discovery = json.loads(
            (high_output / "discovery.json").read_text(encoding="utf-8")
        )
        self.assertEqual(high_discovery["topology"]["tier"], "high_impact")
        self.assertNotEqual(local_discovery["topology"], high_discovery["topology"])
        packets = {path.name for path in (high_output / "operations").glob("*.md")}
        self.assertTrue({
            "dns-inventory-and-cutover.md",
            "mail-routing-cutover.md",
            "mailbox-data-migration.md",
        }.issubset(packets))

    def test_high_impact_environment_selects_high_impact_without_named_operator(self):
        result = self.run_idea_start(
            "--environment", "Production DNS and mail migration."
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        discovery = json.loads(
            (self.output / "discovery.json").read_text(encoding="utf-8")
        )
        self.assertEqual(discovery["topology"]["tier"], "high_impact")
        self.assertIn("DNS", discovery["topology"]["reason"])

    def test_supplied_name_remains_working_candidate_until_evidenced_owner_disposition(self):
        result = self.run_idea_start("--project-name", "Northstar")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        discovery = json.loads(
            (self.output / "discovery.json").read_text(encoding="utf-8")
        )
        self.assertEqual(discovery["identity"], {
            "state": "working_candidate",
            "working_candidate": "Northstar",
            "canonical_name": None,
        })
        packet = (self.output / "NAME-CLEARANCE.md").read_text(encoding="utf-8")
        for source in (
            "github", "pypi", "npm", "crates_io", "com_rdap",
            "web_common_law", "uspto",
        ):
            self.assertIn(f"`{source}`", packet)
        self.assertIn("collect_name_clearance.py", packet)
        self.assertIn("check_name_clearance.py", packet)
        self.assertIn("named-human", packet)
        self.assertIn("explicit later Owner disposition", packet)
        self.assertIn("before the first public repository slug", packet)

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

    def test_malformed_incomplete_idea_fails_without_output_or_stage(self):
        result = subprocess.run(
            [
                sys.executable, "-B", "-m", "writwall_cli", "start",
                "--non-interactive", "--project-root", str(self.project),
                "--problem", "An incomplete idea.",
                "--agent", "Codex", "--location", "local workstation",
                "--environment", "local repository only",
                "--owner-time", "no", "--confirm-no-secrets",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing idea qualification", result.stderr)
        self.assertFalse(self.output.exists())
        self.assertEqual(
            list(self.project.parent.glob(
                f".{self.project.name}-writwall-bootstrap-stage-*"
            )),
            [],
        )

    def test_whitespace_only_idea_answers_fail_without_output(self):
        result = self.run_idea_start(
            "--intended-user", "   ",
            "--constraint", "",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing idea qualification", result.stderr)
        self.assertFalse(self.output.exists())

    def test_contradictory_idea_qualification_fails_without_output(self):
        result = self.run_idea_start(
            "--constraint", "Production deployment.",
            "--non-goal", "Production deployment.",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contradictory idea qualification", result.stderr)
        self.assertFalse(self.output.exists())

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

    def test_name_clearance_proof_tools_are_canonical_in_emitted_bundle(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        copies = {
            "assets/scripts/collect_name_clearance.py":
                REPO_ROOT / "scripts" / "collect_name_clearance.py",
            "assets/checks/check_name_clearance.py":
                REPO_ROOT / "checks" / "check_name_clearance.py",
            "references/name-clearance.md":
                REPO_ROOT / "docs" / "name-clearance.md",
        }
        for relative, canonical in copies.items():
            bundled = self.output / "writwall-adopt" / relative
            self.assertTrue(bundled.is_file(), relative)
            self.assertEqual(bundled.read_bytes(), canonical.read_bytes(), relative)

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
            starter_module, "_atomic_publish",
            side_effect=OSError("injected rename failure"),
        ):
            with self.assertRaises(starter_module.CoordinatorError) as raised:
                starter_module.write_bootstrap(self.project, args, state, ())
        self.assertIn("before atomic publication", str(raised.exception))
        self.assertFalse(self.output.exists())
        self.assertEqual(list(self.project.parent.glob(stage_pattern)), [])

    def test_destination_appearing_during_publication_is_never_replaced(self):
        args = SimpleNamespace(
            project_name="Example", purpose="Example purpose", agent="Codex",
            location="desktop", environment="local repository", owner_time="no",
            scenario=None,
        )
        state = starter_module.ObservedState(
            "clean_new", ("activation pointer is absent",)
        )
        actual_publish = starter_module._atomic_publish

        def competing_publication(stage: Path, output: Path) -> None:
            output.mkdir()
            actual_publish(stage, output)

        with mock.patch.object(
            starter_module, "_atomic_publish", side_effect=competing_publication
        ):
            with self.assertRaises(starter_module.CoordinatorError) as raised:
                starter_module.write_bootstrap(self.project, args, state, ())
        self.assertIn(
            "Writwall published no target; an independently existing destination may remain",
            str(raised.exception),
        )
        self.assertTrue(self.output.is_dir())
        self.assertEqual(list(self.output.iterdir()), [])
        self.assertEqual(list(self.project.parent.glob(
            f".{self.project.name}-writwall-bootstrap-stage-*"
        )), [])

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

    def test_interactive_unnamed_idea_is_qualified_one_question_at_a_time(self):
        answers = (
            "no\n" "yes\n" "\n" "\n"
            "Important decisions disappear before implementation.\n"
            "Technical founders.\n"
            "Rework is costly.\n"
            "Two failed prototypes; demand is assumed.\n"
            "A ratifiable discovery packet.\n"
            "Owner can approve or stop.\n"
            "Local-only.\n"
            "No deployment.\n"
            "May be too heavy.\n"
            "Stop if no useful outcome emerges.\n"
            "A written brief.\n"
            "\n" "\n" "\n" "\n"
        )
        result = subprocess.run(
            [sys.executable, "-B", "-m", "writwall_cli", "start",
             "--project-root", str(self.project)],
            cwd=REPO_ROOT,
            input=answers,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        prompts = (
            "Problem or opportunity", "Intended user", "Why the outcome matters",
            "Current evidence and assumptions", "Smallest useful outcome",
            "Success signal", "Constraints", "Non-goals", "Material risks",
            "Stop or kill conditions", "Existing assets",
        )
        positions = [result.stdout.index(prompt) for prompt in prompts]
        self.assertEqual(positions, sorted(positions))
        discovery = json.loads(
            (self.output / "discovery.json").read_text(encoding="utf-8")
        )
        self.assertEqual(discovery["identity"]["state"], "unnamed")

    def test_brief_file_is_read_but_never_modified(self):
        brief = self.temp / "brief.md"
        brief.write_text("A supplied project thesis.\n", encoding="utf-8")
        result = self.run_start("--brief-file", str(brief))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(brief.read_text(encoding="utf-8"),
                         "A supplied project thesis.\n")
        self.assertEqual(self.intake()["purpose"], "A supplied project thesis.")

    def test_existing_brief_emits_architect_packets_with_explicit_unknowns(self):
        brief = self.temp / "architect-brief.md"
        brief.write_text("A supplied project thesis.\n", encoding="utf-8")
        result = self.run_start("--brief-file", str(brief))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        discovery = json.loads(
            (self.output / "discovery.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            discovery["qualification"]["problem_or_opportunity"],
            "A supplied project thesis.",
        )
        self.assertIsNone(discovery["qualification"]["intended_user"])
        for relative in (
            "OWNER-AGENT.md", "REPOSITORY-OPERATOR.md", "REVIEWER.md",
            "NAME-CLEARANCE.md", "OWNER-RATIFICATION.md",
        ):
            self.assertTrue((self.output / relative).is_file(), relative)

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
