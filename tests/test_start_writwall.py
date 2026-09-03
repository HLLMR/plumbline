# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Public-interface tests for the day-zero Writwall coordinator."""

from __future__ import annotations

import json
import os
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


def ratified_adoption_record(
    *, owner: str = "Test Owner", date: str = "2026-01-01",
    revision: str = "0.8", revision_date: str = "2026-08-21",
    revision_record: str = "decisions/DR-005.md",
    baseline: str = "0" * 40,
    title: str = "# Adoption record",
) -> str:
    """A complete, well-formed, signed Appendix D record.

    This is the deterministic ratified shape: an adoption title, all of
    D.1-D.9, a concrete D.2 baseline commit with adoption-effective
    language, a D.3 revision, and a dated Owner Signature. It matches the
    established shape of this repository's own `governance/decisions/DR-001.md`.
    """
    return f"""{title}

## D.1 Date and Owner

{date} · Owner: {owner}

## D.2 Pre-adoption baseline commit

`{baseline}` — baseline commit. Adoption became effective at this commit.

## D.3 Doctrine revision bound

Revision **{revision}**, ratified **{revision_date}** by `{revision_record}`.

## D.4 Enforcement at adoption

Observed enforcement surfaces at adoption.

## D.5 Conformance gate during the pilot

Reviewer-only controlled inference.

## D.6 Recognized controlling sources at adoption

Disposed by the Owner.

## D.7 Pilot period

10 counted work orders.

## D.8 Reasoning: why adopt, and why now

Recorded by the Owner.

## D.9 Rejected alternatives

1. Alternative rejected.

## Signature

{owner} — Owner — {date}
"""


def draft_adoption_record() -> str:
    """Complete Appendix D section shape, but explicitly unsigned/proposed."""
    return """# Adoption record

## D.1 Date and Owner

DRAFT — Owner: TBD

## D.2 Pre-adoption baseline commit

Proposed baseline; not yet selected.

## D.3 Doctrine revision bound

Revision **0.8**, PROPOSED.

## D.4 Enforcement at adoption

Draft enforcement notes.

## D.5 Conformance gate during the pilot

Draft conformance notes.

## D.6 Recognized controlling sources at adoption

Draft mapping.

## D.7 Pilot period

Draft pilot period.

## D.8 Reasoning: why adopt, and why now

Draft reasoning.

## D.9 Rejected alternatives

Draft rejected alternatives.
"""


def unrelated_ratified_decision() -> str:
    """A signed, ratified decision that is not an Appendix D adoption record.

    Used both at an unrelated path (to prove it cannot lend adoption
    authority to a draft record elsewhere) and at the exact adoption-record
    path itself (to prove a filename alone, even carrying a real Signature,
    is never adoption authority).
    """
    return """# DR-001: Naming decision

Ratified by the Owner on 2026-01-01. This record ratifies a project naming
choice; it is not an adoption record and contains no Appendix D sections.

## Signature

Test Owner — Owner — 2026-01-01
"""


class StartWritwallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.temp, True)
        self.project = self.temp / "project"
        self.project.mkdir()
        self.state = self.temp / "state"

    def environment(self) -> dict[str, str]:
        environment = os.environ.copy()
        environment["WRITWALL_STATE_HOME"] = str(self.state)
        return environment

    def run_start(self, *extra: str, project: Path | None = None):
        return subprocess.run(
            [
                sys.executable,
                "-B",
                "-m",
                "writwall_cli",
                "start",
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
            env=self.environment(),
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
            env=self.environment(),
            capture_output=True,
            text=True,
            timeout=60,
        )

    def run_lifecycle_start(self, project: Path | None = None):
        return subprocess.run(
            [
                sys.executable, "-B", "-m", "writwall_cli", "start",
                "--project-root", str(project or self.project),
            ],
            cwd=REPO_ROOT,
            env=self.environment(),
            capture_output=True,
            text=True,
            timeout=60,
        )

    @staticmethod
    def tree_snapshot(root: Path) -> dict[str, bytes | None]:
        return {
            path.relative_to(root).as_posix(): (
                path.read_bytes() if path.is_file() else None
            )
            for path in sorted(root.rglob("*"))
        }

    @property
    def output(self) -> Path:
        return self.project / ".writwall-bootstrap"

    def intake(self) -> dict:
        return json.loads((self.output / "intake.json").read_text(encoding="utf-8"))

    def handoff(self) -> str:
        return (self.output / "HANDOFF.md").read_text(encoding="utf-8")

    def assert_contains_canonical_root(self, text: str, root: Path, label: str) -> None:
        """Accept either native or portable rendering of one resolved root."""
        native = str(root)
        posix = root.as_posix()
        self.assertTrue(
            native in text or posix in text,
            f"{label} does not carry the canonical project root {root!s}",
        )

    def git(self, *args: str, cwd: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30,
        )

    def make_git_worktree(self, repo_name: str, worktree_name: str,
                          branch: str) -> Path:
        """Build a minimal seeded repository plus one linked worktree.

        Skips the calling test outright when a local git executable is
        unavailable; otherwise returns the worktree top-level path.
        """
        repo = self.temp / repo_name
        repo.mkdir()
        init = self.git("init", "--quiet", cwd=repo)
        if init.returncode != 0:
            self.skipTest(f"git unavailable: {init.stderr}")
        self.git("config", "user.email", "test@example.invalid", cwd=repo)
        self.git("config", "user.name", "Test", cwd=repo)
        (repo / "README.md").write_text("seed\n", encoding="utf-8")
        self.git("add", "README.md", cwd=repo)
        commit = self.git("commit", "--quiet", "-m", "seed", cwd=repo)
        self.assertEqual(commit.returncode, 0, commit.stdout + commit.stderr)
        worktree = self.temp / worktree_name
        add = self.git(
            "worktree", "add", "--quiet", str(worktree), "-b", branch, cwd=repo,
        )
        self.assertEqual(add.returncode, 0, add.stdout + add.stderr)
        return worktree

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
            [sys.executable, "-m", "venv", "--without-pip", str(venv)],
            check=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        python = venv / ("Scripts/python.exe" if sys.platform == "win32"
                         else "bin/python")
        install = subprocess.run(
            [
                sys.executable, "-m", "pip", "--python", str(python),
                "install", "--no-deps", str(wheels[0]),
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
            env=self.environment(),
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
            env=self.environment(),
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

    def test_isolated_install_emits_no_bytecode_residue_under_normal_environment(self):
        command = self.install_writwall()
        environment = self.environment()
        environment.pop("PYTHONDONTWRITEBYTECODE", None)
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
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        cache_dirs = sorted(
            path.relative_to(self.output).as_posix()
            for path in self.output.rglob("__pycache__") if path.is_dir()
        )
        bytecode_files = sorted(
            path.relative_to(self.output).as_posix()
            for path in self.output.rglob("*.pyc") if path.is_file()
        )
        self.assertEqual(cache_dirs, [])
        self.assertEqual(bytecode_files, [])

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
        self.assertIn("Architect", local_discovery["topology"]["roles"])
        self.assertIn("General", local_discovery["topology"]["roles"])
        self.assertIn("repository Operator", local_discovery["topology"]["roles"])
        self.assertNotIn(
            "Owner-Agent architect/coordinator",
            local_discovery["topology"]["roles"],
        )

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

    def test_existing_bootstrap_routes_to_recovery_without_overwrite(self):
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_text("unchanged", encoding="utf-8")
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "unchanged")
        self.assertEqual(sorted(p.name for p in self.output.iterdir()), ["keep.txt"])
        self.assertIn("Observed lifecycle state: partial_bootstrap", result.stdout)
        self.assertIn("Act as a fresh recovery coordinator", result.stdout)

    def test_lifecycle_change_during_interactive_intake_stops_before_any_write(self):
        process = subprocess.Popen(
            [
                sys.executable, "-B", "-m", "writwall_cli", "start",
                "--structured-intake",
                "--project-root", str(self.project),
                "--project-name", "Example project",
                "--purpose", "Build a small, governed project.",
                "--agent", "Codex",
                "--location", "local workstation",
                "--environment", "local repository only",
            ],
            cwd=REPO_ROOT,
            env=self.environment(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        assert process.stdout is not None
        prompt = ""
        while "Track Owner active minutes?" not in prompt:
            char = process.stdout.read(1)
            if not char:
                break
            prompt += char
        self.assertIn("Track Owner active minutes?", prompt)

        governance = self.project / "governance"
        decisions = governance / "decisions"
        decisions.mkdir(parents=True)
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(f"# {name}\n", encoding="utf-8")
        (decisions / "DR-001.md").write_text(
            draft_adoption_record(), encoding="utf-8"
        )
        changed_state = self.tree_snapshot(self.project)

        stdout_tail, stderr = process.communicate("no\nyes\n\n\n", timeout=60)
        self.assertNotEqual(process.returncode, 0, prompt + stdout_tail + stderr)
        self.assertEqual(self.tree_snapshot(self.project), changed_state)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.state.exists())
        self.assertIn("lifecycle changed during intake", stderr)

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
            env=self.environment(),
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
            env=self.environment(),
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
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.state.exists())
        self.assertIn("Observed lifecycle state: active_work_order", result.stdout)
        self.assertIn("Act as a fresh Implementer for the active work order only", result.stdout)

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
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertIn(
            "activation pointer does not identify the only ACTIVE work order",
            result.stderr,
        )

    def test_missing_pointer_with_closed_history_never_emits_resume_prompt(self):
        closed = self.project / "governance" / "history" / "WO-001.md"
        closed.parent.mkdir(parents=True)
        closed.write_text("---\nid: WO-001\nstatus: CLOSED\n---\n", encoding="utf-8")
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (self.project / "governance" / name).write_text(f"# {name}\n", encoding="utf-8")
        decision = self.project / "governance" / "decisions" / "DR-001.md"
        decision.parent.mkdir(parents=True)
        decision.write_text(ratified_adoption_record(), encoding="utf-8")
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.state.exists())
        self.assertIn("Observed lifecycle state: retired_lockout", result.stdout)
        self.assertIn("Act as a fresh General", result.stdout)
        self.assertIn("General", result.stdout)
        self.assertNotIn("Owner-Agent / Project-Architect", result.stdout)
        self.assertNotIn("resume", result.stdout.lower())
        self.assertNotIn("Act as a fresh Implementer", result.stdout)

    def test_pointer_to_closed_order_is_inconsistent_and_creates_nothing(self):
        work_order = self.project / "governance" / "work-orders" / "WO-001.md"
        work_order.parent.mkdir(parents=True)
        work_order.write_text("---\nid: WO-001\nstatus: CLOSED\n---\n", encoding="utf-8")
        pointer = self.project / ".claude" / "active-wo.txt"
        pointer.parent.mkdir(parents=True)
        pointer.write_text("governance/work-orders/WO-001.md\n", encoding="utf-8")
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertIn(
            "activation pointer resolves, but the work order status is 'CLOSED', not 'ACTIVE'",
            result.stderr,
        )

    def test_partial_bootstrap_routes_to_recovery_coordinator(self):
        settings = self.project / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text("{}\n", encoding="utf-8")
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.state.exists())
        self.assertIn("Observed lifecycle state: partial_bootstrap", result.stdout)
        self.assertIn("Act as a fresh recovery coordinator", result.stdout)

    def test_partial_bootstrap_directory_routes_without_republication(self):
        self.output.mkdir()
        sentinel = self.output / "HANDOFF.md"
        sentinel.write_text("incomplete bootstrap\n", encoding="utf-8")
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "incomplete bootstrap\n")
        self.assertFalse(self.state.exists())
        self.assertIn("Observed lifecycle state: partial_bootstrap", result.stdout)
        self.assertIn("Act as a fresh recovery coordinator", result.stdout)

    def test_bootstrap_mixed_with_established_lifecycle_fails_closed(self):
        for lifecycle in ("active", "adopted", "retired"):
            with self.subTest(lifecycle=lifecycle):
                project = self.temp / f"project-{lifecycle}"
                project.mkdir()
                bootstrap = project / ".writwall-bootstrap"
                bootstrap.mkdir()
                (bootstrap / "HANDOFF.md").write_text(
                    "incomplete bootstrap\n", encoding="utf-8"
                )
                governance = project / "governance"
                if lifecycle == "active":
                    order = governance / "work-orders" / "WO-001.md"
                    order.parent.mkdir(parents=True)
                    order.write_text(
                        "---\nid: WO-001\nstatus: ACTIVE\n---\n", encoding="utf-8"
                    )
                    pointer = project / ".claude" / "active-wo.txt"
                    pointer.parent.mkdir(parents=True)
                    pointer.write_text(
                        "governance/work-orders/WO-001.md\n", encoding="utf-8"
                    )
                else:
                    governance.mkdir()
                    for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
                        (governance / name).write_text(
                            f"# {name}\n", encoding="utf-8"
                        )
                    if lifecycle == "adopted":
                        decision = governance / "decisions" / "DR-001.md"
                        decision.parent.mkdir()
                        decision.write_text(ratified_adoption_record(), encoding="utf-8")
                    else:
                        decision = governance / "decisions" / "DR-001.md"
                        decision.parent.mkdir()
                        decision.write_text(ratified_adoption_record(), encoding="utf-8")
                        closed = governance / "history" / "WO-001.md"
                        closed.parent.mkdir()
                        closed.write_text(
                            "---\nid: WO-001\nstatus: CLOSED\n---\n",
                            encoding="utf-8",
                        )

                before = self.tree_snapshot(project)
                result = self.run_lifecycle_start(project)
                self.assertNotEqual(
                    result.returncode, 0, result.stdout + result.stderr
                )
                self.assertEqual(self.tree_snapshot(project), before)
                self.assertFalse(self.state.exists())
                self.assertIn("inconsistent state", result.stderr)
                self.assertIn(".writwall-bootstrap", result.stderr)

    def test_adopted_lockout_routes_to_fresh_general(self):
        governance = self.project / "governance"
        governance.mkdir()
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(f"# {name}\n", encoding="utf-8")
        decision = governance / "decisions" / "DR-001.md"
        decision.parent.mkdir()
        decision.write_text(ratified_adoption_record(), encoding="utf-8")
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.state.exists())
        self.assertIn("Observed lifecycle state: adopted_lockout", result.stdout)
        self.assertIn("Act as a fresh General", result.stdout)
        self.assertNotIn("Owner-Agent / Project-Architect", result.stdout)
        flat = " ".join(result.stdout.split())
        self.assertIn("Recommendation and material tradeoff", flat)
        self.assertIn("supporting evidence", flat)
        self.assertIn("one combined disposition and action", flat)
        self.assertIn("explicitly include creation and dispatch", flat)
        self.assertIn("Do not ask for the same decision again", flat)
        self.assertIn("perform every mechanically available authorized step", flat)

    def test_draft_adoption_record_with_closed_history_never_reports_adopted_or_retired(self):
        governance = self.project / "governance"
        governance.mkdir()
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(f"# {name}\n", encoding="utf-8")
        decisions = governance / "decisions"
        decisions.mkdir(parents=True)
        (decisions / "DR-001.md").write_text(draft_adoption_record(), encoding="utf-8")
        (decisions / "DR-999-unrelated.md").write_text(
            unrelated_ratified_decision(), encoding="utf-8"
        )
        closed = governance / "history" / "WO-001.md"
        closed.parent.mkdir(parents=True)
        closed.write_text("---\nid: WO-001\nstatus: CLOSED\n---\n", encoding="utf-8")
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.state.exists())
        self.assertNotIn("Observed lifecycle state: adopted_lockout", result.stdout)
        self.assertNotIn("Observed lifecycle state: retired_lockout", result.stdout)
        self.assertIn("Observed lifecycle state: partial_bootstrap", result.stdout)

    def test_signed_unrelated_decision_at_exact_adoption_path_fails_closed(self):
        governance = self.project / "governance"
        governance.mkdir()
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(f"# {name}\n", encoding="utf-8")
        decisions = governance / "decisions"
        decisions.mkdir(parents=True)
        (decisions / "DR-001.md").write_text(
            unrelated_ratified_decision(), encoding="utf-8"
        )
        closed = governance / "history" / "WO-001.md"
        closed.parent.mkdir(parents=True)
        closed.write_text("---\nid: WO-001\nstatus: CLOSED\n---\n", encoding="utf-8")
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertFalse(self.state.exists())
        self.assertNotIn("Observed lifecycle state: adopted_lockout", result.stdout)
        self.assertNotIn("Observed lifecycle state: retired_lockout", result.stdout)
        self.assertIn("inconsistent state", result.stderr)
        self.assertIn("does not carry", result.stderr)
        self.assertIn("adoption-record title", result.stderr)
        # Nondisclosing: the diagnostic names the path, never the document body.
        self.assertNotIn("Test Owner", result.stderr)
        self.assertNotIn("Naming decision", result.stderr)

    def test_adopted_lockout_requires_ratified_evidence_not_mere_filename(self):
        governance = self.project / "governance"
        governance.mkdir()
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(f"# {name}\n", encoding="utf-8")
        decision = governance / "decisions" / "DR-001.md"
        decision.parent.mkdir(parents=True)
        decision.write_text("# Adoption record\n", encoding="utf-8")
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertNotIn("Observed lifecycle state: adopted_lockout", result.stdout)
        self.assertIn("inconsistent state", result.stderr)
        self.assertIn("missing required Appendix D section", result.stderr)

    def test_retired_lockout_requires_ratified_adoption_evidence(self):
        governance = self.project / "governance"
        governance.mkdir()
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(f"# {name}\n", encoding="utf-8")
        closed = governance / "history" / "WO-001.md"
        closed.parent.mkdir(parents=True)
        closed.write_text("---\nid: WO-001\nstatus: CLOSED\n---\n", encoding="utf-8")
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertNotIn("Observed lifecycle state: retired_lockout", result.stdout)
        self.assertIn("Observed lifecycle state: partial_bootstrap", result.stdout)

    def test_alternate_adoption_record_path_routes_to_adopted_lockout(self):
        governance = self.project / "governance"
        governance.mkdir()
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(f"# {name}\n", encoding="utf-8")
        (governance / "ADOPTION-RECORD.md").write_text(
            ratified_adoption_record(title="# Adoption record (alternate path)"),
            encoding="utf-8",
        )
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertIn("Observed lifecycle state: adopted_lockout", result.stdout)

    def test_contradictory_coexisting_adoption_records_fail_closed(self):
        governance = self.project / "governance"
        governance.mkdir()
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(f"# {name}\n", encoding="utf-8")
        decisions = governance / "decisions"
        decisions.mkdir(parents=True)
        (decisions / "DR-001.md").write_text(ratified_adoption_record(), encoding="utf-8")
        (governance / "ADOPTION-RECORD.md").write_text(
            ratified_adoption_record(
                title="# Adoption record (alternate path)", revision="0.6",
            ),
            encoding="utf-8",
        )
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertIn("inconsistent state", result.stderr)
        self.assertIn("contradictory", result.stderr)

    def test_contradictory_baseline_between_coexisting_adoption_records_fails_closed(self):
        governance = self.project / "governance"
        governance.mkdir()
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(f"# {name}\n", encoding="utf-8")
        decisions = governance / "decisions"
        decisions.mkdir(parents=True)
        (decisions / "DR-001.md").write_text(ratified_adoption_record(), encoding="utf-8")
        (governance / "ADOPTION-RECORD.md").write_text(
            ratified_adoption_record(
                title="# Adoption record (alternate path)", baseline="1" * 40,
            ),
            encoding="utf-8",
        )
        before = self.tree_snapshot(self.project)
        result = self.run_lifecycle_start()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.tree_snapshot(self.project), before)
        self.assertFalse(self.output.exists())
        self.assertIn("inconsistent state", result.stderr)
        self.assertIn("contradictory", result.stderr)
        self.assertIn("baseline", result.stderr)

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
        scenario_text = combined.replace(
            self.project.resolve().as_posix(), "<canonical-project-root>"
        ).lower()
        self.assertNotIn("fastmail", scenario_text)
        self.assertNotIn("proton", scenario_text)
        self.assertNotIn("hllmr", scenario_text)
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

    def test_clean_new_handoff_routes_bootstrap_charter_addendum(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        handoff = self.handoff()
        self.assertIn(
            ".writwall-bootstrap/writwall-adopt/assets/"
            "bootstrap-charter-addendum.md",
            handoff,
        )
        self.assertIn("Ordinary no-pointer work", handoff)
        self.assertIn("confers no mutation authority", handoff)

    def test_clean_new_handoff_carries_terminal_fresh_architect_prompt(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        handoff = self.handoff()
        self.assertIn("After adoption closeout", handoff)
        self.assertIn(starter_module.PROJECT_ARCHITECT_PROMPT, handoff)
        self.assertIn("onboarding coordinator stops", handoff)

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
        self.assertIn(
            "one human Owner, one Architect, one General, one repository Operator",
            handoff,
        )
        self.assertIn("The Architect may interview", handoff)
        self.assertIn("The General may draft, route", handoff)
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
                starter_module.write_bootstrap(self.project, args, state, (), 1)
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
                starter_module.write_bootstrap(self.project, args, state, (), 1)
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
                "--structured-intake",
                "--project-root", str(self.project),
                "--project-name", "Interactive project",
            ],
            cwd=REPO_ROOT,
            env=self.environment(),
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
             "--structured-intake",
             "--project-root", str(self.project)],
            cwd=REPO_ROOT,
            env=self.environment(),
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

    def test_intake_records_one_resolved_canonical_project_root(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        canonical = self.project.resolve()
        self.assertEqual(self.intake()["project_root"], canonical.as_posix())
        self.assertNotEqual(self.intake()["project_root"], ".")

    def test_discovery_record_carries_the_same_canonical_project_root(self):
        result = self.run_idea_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        canonical = self.project.resolve()
        discovery = json.loads(
            (self.output / "discovery.json").read_text(encoding="utf-8")
        )
        self.assertEqual(discovery.get("project_root"), canonical.as_posix())

    def test_every_generated_role_packet_carries_the_canonical_project_root(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        canonical = self.project.resolve()
        for relative in (
            "HANDOFF.md", "OWNER-AGENT.md", "REPOSITORY-OPERATOR.md",
            "REVIEWER.md", "NAME-CLEARANCE.md", "OWNER-RATIFICATION.md",
        ):
            text = (self.output / relative).read_text(encoding="utf-8")
            self.assert_contains_canonical_root(text, canonical, relative)

    def test_handoff_states_the_no_shadow_repository_no_durable_temp_rule(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        handoff = self.handoff()
        flat = " ".join(handoff.split()).lower()
        self.assertIn("durable project artifacts", flat)
        self.assertIn("never become the authoritative project tree", flat)
        self.assertIn("removed after use", flat)

    def test_operation_packets_carry_root_and_no_shadow_repository_rule(self):
        result = self.run_start("--external-operator", "DNS administration")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        canonical = self.project.resolve()
        packet = (self.output / "operations" / "dns-administration.md").read_text(
            encoding="utf-8"
        )
        self.assert_contains_canonical_root(packet, canonical, "operation packet")
        self.assertIn("shadow", packet.lower())
        self.assertIn("canonical", packet.lower())

    def test_supplied_path_spelling_is_resolved_to_one_canonical_form(self):
        spelled = str(self.project) + os.sep + "." + os.sep
        result = subprocess.run(
            [
                sys.executable, "-B", "-m", "writwall_cli", "start",
                "--non-interactive",
                "--project-root", spelled,
                "--project-name", "Example project",
                "--purpose", "Build a small, governed project.",
                "--agent", "Codex",
                "--location", "local workstation",
                "--environment", "local repository only",
                "--owner-time", "no",
                "--confirm-no-secrets",
            ],
            cwd=REPO_ROOT,
            env=self.environment(),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        canonical = self.project.resolve()
        self.assertEqual(self.intake()["project_root"], canonical.as_posix())

    def test_non_git_project_directory_is_recorded_canonically(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.project / ".git").exists())
        canonical = self.project.resolve()
        self.assertEqual(self.intake()["project_root"], canonical.as_posix())

    def test_git_worktree_top_level_is_recorded_as_its_own_canonical_root(self):
        worktree = self.make_git_worktree(
            "wt-top-repo", "wt-top-worktree", "wt-top-branch"
        )
        result = self.run_start(project=worktree)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        intake = json.loads(
            ((worktree / ".writwall-bootstrap") / "intake.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(intake["project_root"], worktree.resolve().as_posix())

    def test_nested_directory_inside_git_worktree_stops_with_rerun_diagnostic(self):
        worktree = self.make_git_worktree(
            "wt-nested-repo", "wt-nested-worktree", "wt-nested-branch"
        )
        nested = worktree / "nested" / "project"
        nested.mkdir(parents=True)
        before = self.tree_snapshot(worktree)
        result = subprocess.run(
            [
                sys.executable, "-B", "-m", "writwall_cli", "start",
                "--non-interactive",
                "--project-root", str(nested),
                "--project-name", "Example project",
                "--purpose", "Build a small, governed project.",
                "--agent", "Codex",
                "--location", "local workstation",
                "--environment", "local repository only",
                "--owner-time", "no",
                "--confirm-no-secrets",
            ],
            cwd=REPO_ROOT,
            env=self.environment(),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.tree_snapshot(worktree), before)
        self.assertFalse((nested / ".writwall-bootstrap").exists())
        combined = (result.stdout + result.stderr).lower()
        self.assertIn("worktree", combined)
        self.assertIn("rerun", combined)
        self.assert_contains_canonical_root(
            result.stdout + result.stderr, worktree.resolve(),
            "worktree rerun diagnostic",
        )

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

    def test_start_initializes_privacy_without_disclosing_its_location(self):
        result = self.run_idea_start()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        intake = self.intake()
        self.assertTrue(intake["privacy_screen"]["ready"])
        self.assertGreater(intake["privacy_screen"]["entry_count"], 0)
        combined = result.stdout + result.stderr + self.handoff()
        self.assertNotIn(str(self.state), combined)
        self.assert_contains_canonical_root(
            self.handoff(), self.project.resolve(), "HANDOFF.md"
        )
        self.assertEqual(len(list(self.state.rglob("private-patterns.txt"))), 1)

    def test_start_preserves_local_private_identifiers_without_copying_them_to_bootstrap(self):
        private_identifier = "CLIENT-CODENAME-EMBER"
        added = subprocess.run(
            [sys.executable, "-B", "-m", "writwall_cli", "privacy", "add",
             "--project-root", str(self.project), "--identifier-stdin",
             "--confirm-no-secrets"],
            cwd=REPO_ROOT, env=self.environment(), input=private_identifier + "\n",
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(added.returncode, 0, added.stdout + added.stderr)
        result = self.run_idea_start()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        bootstrap_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in self.output.rglob("*") if path.is_file()
        )
        self.assertNotIn(private_identifier, result.stdout + result.stderr)
        self.assertNotIn(private_identifier, bootstrap_text)
        profile = next(self.state.rglob("private-patterns.txt"))
        self.assertIn(private_identifier, profile.read_text(encoding="utf-8"))

    # -- WO-WW-021: conversation-first inception and existing-project
    # continuity. Prove the ordinary bare invocation no longer demands the
    # long structured questionnaire, existing repositories get a bounded
    # local inventory and conversation-first Architect opening, empty
    # projects get one open invitation, structured/non-interactive intake
    # still works and now also emits the Owner/Architect/General/Operator
    # topology, and active work still routes to a bounded Operator/
    # Implementer. Added RED in this work order; now exercised against the
    # GREEN implementation.

    def run_conversation_start(self, *extra: str, project: Path | None = None):
        """The ordinary, low-friction invocation: only --project-root, no
        other intake flags, and no answers available on stdin. Today this
        falls straight into the full interactive questionnaire and crashes
        with EOFError on the first blocking `input()` call; the conversation
        -first coordinator must instead succeed without it.
        """
        return subprocess.run(
            [
                sys.executable, "-B", "-m", "writwall_cli", "start",
                "--project-root", str(project or self.project),
                *extra,
            ],
            cwd=REPO_ROOT,
            env=self.environment(),
            input="",
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_ordinary_project_root_only_invocation_skips_long_questionnaire(self):
        result = self.run_conversation_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        combined = result.stdout + result.stderr
        for legacy_prompt in (
            "Track Owner active minutes?",
            "Continue without entering secrets?",
            "Problem or opportunity",
            "Working candidate name",
        ):
            self.assertNotIn(legacy_prompt, combined)

    def test_existing_git_repository_yields_bounded_local_observations_and_architect_opening(self):
        init = self.git("init", "--quiet", cwd=self.project)
        if init.returncode != 0:
            self.skipTest(f"git unavailable: {init.stderr}")
        self.git("config", "user.email", "test@example.invalid", cwd=self.project)
        self.git("config", "user.name", "Test", cwd=self.project)
        (self.project / "README.md").write_text("An existing project.\n", encoding="utf-8")
        self.git("add", "README.md", cwd=self.project)
        commit = self.git(
            "commit", "--quiet", "-m", "Seed existing project inventory marker",
            cwd=self.project,
        )
        self.assertEqual(commit.returncode, 0, commit.stdout + commit.stderr)
        branch = self.git("branch", "--show-current", cwd=self.project).stdout.strip()
        self.assertTrue(branch)

        # A direct ordinary Git repository root (not a linked or nested
        # worktree) used as the project root itself.
        result = self.run_conversation_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        combined = result.stdout + result.stderr + self.handoff()
        self.assertIn(branch, combined)
        self.assertIn("Seed existing project inventory marker", combined)
        self.assertIn("clean", combined.lower())
        self.assertIn("read-only", combined.lower())
        self.assertTrue(
            "explore" in combined.lower() or "start elsewhere" in combined.lower(),
            combined,
        )

    def test_empty_new_project_receives_open_conversational_invitation(self):
        result = self.run_conversation_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        combined = result.stdout + result.stderr + self.handoff()
        self.assertIn("Tell me what you are thinking", combined)
        self.assertNotIn("Problem or opportunity", combined)
        self.assertNotIn("Working candidate name", combined)

    def test_conversation_first_partial_idea_flags_keep_validation(self):
        result = self.run_conversation_start(
            "--problem", "A stated problem without the remaining qualification.",
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("missing idea qualification", result.stderr)
        self.assertFalse(self.output.exists())

    def test_conversation_first_contradictory_idea_flags_keep_validation(self):
        flags = [
            "--problem", "A fully stated idea.",
            "--intended-user", "The Owner.",
            "--why-matters", "It avoids drift.",
            "--evidence", "A concrete observed failure.",
            "--smallest-outcome", "One bounded fix.",
            "--success-signal", "The regression stays green.",
            "--constraint", "Do not publish.",
            "--non-goal", "Do not publish.",
            "--risk", "The intake could overreach.",
            "--kill-condition", "Stop on ambiguity.",
            "--asset", "The existing repository.",
        ]
        result = self.run_conversation_start(*flags)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("contradictory idea qualification", result.stderr)
        self.assertFalse(self.output.exists())

    def test_structured_non_interactive_intake_still_emits_new_role_topology(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.output / "ARCHITECT.md").is_file())
        self.assertTrue((self.output / "GENERAL.md").is_file())
        self.assertTrue((self.output / "OPERATOR.md").is_file())
        self.assertTrue((self.output / "REPOSITORY-OPERATOR.md").is_file())
        self.assertTrue((self.output / "REVIEWER.md").is_file())

    def test_legacy_role_packet_names_remain_as_documented_compatibility_aliases(self):
        result = self.run_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        owner_agent = (self.output / "OWNER-AGENT.md").read_text(encoding="utf-8")
        repository_operator = (self.output / "REPOSITORY-OPERATOR.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("compatibility alias", owner_agent.lower())
        self.assertIn("Architect", owner_agent)
        self.assertIn("compatibility alias", repository_operator.lower())
        self.assertIn("Operator", repository_operator)

    def test_active_work_order_routes_to_bounded_operator_implementer(self):
        work_order = self.project / "governance" / "work-orders" / "WO-001.md"
        work_order.parent.mkdir(parents=True)
        work_order.write_text(
            "---\nid: WO-001\nstatus: ACTIVE\n---\n# Work\n", encoding="utf-8"
        )
        pointer = self.project / ".claude" / "active-wo.txt"
        pointer.parent.mkdir(parents=True)
        pointer.write_text("governance/work-orders/WO-001.md\n", encoding="utf-8")
        result = self.run_lifecycle_start()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Observed lifecycle state: active_work_order", result.stdout)
        self.assertIn("Operator", result.stdout)


if __name__ == "__main__":
    unittest.main()
