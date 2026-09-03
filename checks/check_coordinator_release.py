# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Install and smoke-test Writwall from an external release candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path


REQUIRED_CANDIDATE_PATHS = (
    "pyproject.toml",
    "writwall_cli/__init__.py",
    "writwall_cli/__main__.py",
    "writwall_cli/coordinator.py",
    "scripts/start_writwall.py",
    "scripts/privacy_screen.py",
    "skills/writwall-adopt/SKILL.md",
)
REQUIRED_HANDOFF_PATHS = (
    "HANDOFF.md",
    "intake.json",
    "ARCHITECT.md",
    "GENERAL.md",
    "OPERATOR.md",
    "OWNER-AGENT.md",
    "REPOSITORY-OPERATOR.md",
    "REVIEWER.md",
    "NAME-CLEARANCE.md",
    "OWNER-RATIFICATION.md",
    "writwall-adopt/SKILL.md",
    "writwall-adopt/assets/bootstrap-charter-addendum.md",
    "writwall-adopt/assets/scripts/collect_name_clearance.py",
    "writwall-adopt/assets/checks/check_name_clearance.py",
    "writwall-adopt/references/name-clearance.md",
)


class ReleaseCheckError(RuntimeError):
    """A bounded, user-facing release-candidate failure."""


RATIFIED_ADOPTION_RECORD = """# Adoption record

## D.1 Date and Owner

2026-01-01 · Owner: Example Owner

## D.2 Pre-adoption baseline commit

`0000000000000000000000000000000000000000` — baseline commit. Adoption
became effective at this commit.

## D.3 Doctrine revision bound

Revision **0.8**, ratified **2026-01-01** by `decisions/DR-EXAMPLE.md`.

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

Example Owner — Owner — 2026-01-01
"""

DRAFT_ADOPTION_RECORD = """# Adoption record

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

UNRELATED_RATIFIED_DECISION = """# DR-001: Naming decision

Ratified by the Owner on 2026-01-01. This record ratifies a project naming
choice; it is not an adoption record and contains no Appendix D sections.

## Signature

Example Owner — Owner — 2026-01-01
"""


def tree_digest(root: Path) -> str:
    lines: list[str] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def run(command: list[str], *, cwd: Path, environment: dict[str, str],
        label: str, timeout: int = 180,
        closed_stdin: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        stdin=subprocess.DEVNULL if closed_stdin else None,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode:
        detail = (result.stdout + result.stderr).strip()
        raise ReleaseCheckError(
            f"{label} failed with exit {result.returncode}"
            + (f": {detail}" if detail else "")
        )
    return result


def installed_command(venv: Path) -> Path:
    if os.name == "nt":
        return venv / "Scripts" / "writwall.exe"
    return venv / "bin" / "writwall"


def verify_installed_version(installed: str, expected: str) -> None:
    if installed != expected:
        raise ReleaseCheckError(
            f"installed version {installed!r} does not match candidate {expected!r}"
        )


def verify_expected_tag(candidate_version: str, expected_tag: str) -> None:
    if re.fullmatch(
        r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)",
        expected_tag,
    ) is None:
        raise ReleaseCheckError(
            "intended tag is not canonical vMAJOR.MINOR.PATCH"
        )
    if expected_tag.removeprefix("v") != candidate_version:
        raise ReleaseCheckError(
            f"candidate version {candidate_version!r} does not match intended "
            f"tag {expected_tag!r}"
        )


def verify_candidate_unchanged(candidate: Path, before: str) -> None:
    if tree_digest(candidate) != before:
        raise ReleaseCheckError("candidate changed during the release check")


def python_bytecode_residue(root: Path) -> list[str]:
    """Return non-canonical interpreter residue from a generated handoff."""
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if (
            any(part.casefold() == "__pycache__" for part in path.relative_to(root).parts)
            or path.suffix.casefold() == ".pyc"
        )
    )


def check_candidate(candidate: Path, expected_tag: str) -> None:
    candidate = candidate.resolve()
    if not candidate.is_dir():
        raise ReleaseCheckError("candidate contract failed: directory is absent")
    missing = [relative for relative in REQUIRED_CANDIDATE_PATHS
               if not (candidate / relative).is_file()]
    if missing:
        raise ReleaseCheckError(
            "candidate contract failed; missing: " + ", ".join(missing)
        )
    with (candidate / "pyproject.toml").open("rb") as handle:
        expected_version = tomllib.load(handle)["project"]["version"]
    verify_expected_tag(expected_version, expected_tag)

    before = tree_digest(candidate)
    with tempfile.TemporaryDirectory(prefix="writwall-release-check-") as raw:
        workspace = Path(raw).resolve()
        source = workspace / "source"
        shutil.copytree(candidate, source)
        wheelhouse = workspace / "wheelhouse"
        wheelhouse.mkdir()
        venv = workspace / "venv"
        project = workspace / "external-project"
        project.mkdir()
        state = workspace / "state"

        environment = os.environ.copy()
        environment.update({
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_INDEX": "1",
            "WRITWALL_STATE_HOME": str(state),
        })
        environment.pop("PYTHONDONTWRITEBYTECODE", None)
        run(
            [
                sys.executable, "-m", "pip", "wheel", "--no-deps",
                "--no-build-isolation", "--wheel-dir", str(wheelhouse),
                str(source),
            ],
            cwd=workspace,
            environment=environment,
            label="wheel build",
        )
        wheels = sorted(wheelhouse.glob("writwall-*.whl"))
        if len(wheels) != 1:
            raise ReleaseCheckError(
                f"wheel build produced {len(wheels)} writwall wheels; expected one"
            )

        run(
            [sys.executable, "-m", "venv", "--without-pip", str(venv)],
            cwd=workspace,
            environment=environment,
            label="virtual environment creation",
        )
        command = installed_command(venv)
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        run(
            [
                sys.executable, "-m", "pip", "--python", str(python),
                "install", "--no-deps", str(wheels[0]),
            ],
            cwd=workspace,
            environment=environment,
            label="wheel installation",
        )
        version = run(
            [
                str(python), "-c",
                "import importlib.metadata; print(importlib.metadata.version('writwall'))",
            ],
            cwd=workspace,
            environment=environment,
            label="installed version",
        ).stdout.strip()
        verify_installed_version(version, expected_version)
        help_result = run(
            [str(command), "start", "--help"],
            cwd=workspace,
            environment=environment,
            label="installed help",
        )
        if "Start with an idea" not in help_result.stdout:
            raise ReleaseCheckError("installed help omitted the coordinator promise")

        conversation_project = workspace / "conversation-first-project"
        conversation_project.mkdir()
        run(
            [
                str(command), "start",
                "--project-root", str(conversation_project),
            ],
            cwd=workspace,
            environment=environment,
            label="installed conversation-first run",
            closed_stdin=True,
        )
        conversation_output = conversation_project / ".writwall-bootstrap"
        conversation_handoff = conversation_output / "HANDOFF.md"
        conversation_architect = conversation_output / "ARCHITECT.md"
        if not conversation_handoff.is_file() or not conversation_architect.is_file():
            raise ReleaseCheckError(
                "complete handoff failed: installed conversation-first run omitted "
                "HANDOFF.md or ARCHITECT.md"
            )
        conversation_text = conversation_handoff.read_text(encoding="utf-8")
        required_conversation_text = (
            "Fresh Architect (conversation-first)",
            'Open with exactly: "Tell me what you are thinking."',
        )
        missing_conversation_text = [
            text for text in required_conversation_text
            if text not in conversation_text
        ]
        if missing_conversation_text:
            raise ReleaseCheckError(
                "installed conversation-first handoff omitted: "
                + ", ".join(missing_conversation_text)
            )
        conversation_residue = python_bytecode_residue(conversation_output)
        if conversation_residue:
            raise ReleaseCheckError(
                "conversation-first handoff contains Python bytecode residue: "
                + ", ".join(conversation_residue)
            )

        run(
            [
                str(command), "start", "--non-interactive",
                "--project-root", str(project),
                "--problem", "A small external project needs bounded agent work.",
                "--intended-user", "A first-time Writwall adopter.",
                "--why-matters", "The first handoff must be usable without prior context.",
                "--evidence", "Release readiness remains unproven outside source tests.",
                "--smallest-outcome", "A complete create-only adoption handoff.",
                "--success-signal", "Every promised packet is present and readable.",
                "--constraint", "No network or external-system mutation.",
                "--non-goal", "No project adoption or implementation.",
                "--risk", "Packaging may omit a required bootstrap asset.",
                "--kill-condition", "Stop if any required packet is absent.",
                "--asset", "The checked Writwall release candidate.",
                "--agent", "fresh Owner-Agent",
                "--location", "outside the walled project session",
                "--environment", "disposable local external project",
                "--owner-time", "no",
                "--confirm-no-secrets",
            ],
            cwd=workspace,
            environment=environment,
            label="installed coordinator run",
        )
        output = project / ".writwall-bootstrap"
        missing_handoff = [relative for relative in REQUIRED_HANDOFF_PATHS
                           if not (output / relative).is_file()]
        if missing_handoff:
            raise ReleaseCheckError(
                "complete handoff failed; missing: " + ", ".join(missing_handoff)
            )
        residue = python_bytecode_residue(output)
        if residue:
            raise ReleaseCheckError(
                "complete handoff contains Python bytecode residue: "
                + ", ".join(residue)
            )

        intake_payload = json.loads(
            (output / "intake.json").read_text(encoding="utf-8")
        )
        recorded_root = intake_payload.get("project_root")
        expected_root = project.resolve().as_posix()
        if recorded_root in (None, ".", ""):
            raise ReleaseCheckError(
                "installed coordinator recorded no canonical root evidence: "
                f"project_root={recorded_root!r}"
            )
        if recorded_root != expected_root:
            raise ReleaseCheckError(
                f"installed coordinator recorded canonical root {recorded_root!r}, "
                f"expected {expected_root!r}"
            )

        adopted = workspace / "adopted-project"
        governance = adopted / "governance"
        decisions = governance / "decisions"
        decisions.mkdir(parents=True)
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (governance / name).write_text(
                f"# {name}\n", encoding="utf-8", newline="\n"
            )
        (decisions / "DR-001.md").write_text(
            RATIFIED_ADOPTION_RECORD, encoding="utf-8", newline="\n"
        )
        adopted_before = tree_digest(adopted)
        adopted_result = run(
            [str(command), "start", "--project-root", str(adopted)],
            cwd=workspace,
            environment=environment,
            label="installed adopted-lockout route",
        )
        required_route_text = (
            "Observed lifecycle state: adopted_lockout",
            "Act as a fresh General",
            "one combined disposition and action",
            "Do not ask for the same decision again",
        )
        route_output = " ".join(adopted_result.stdout.split())
        missing_route_text = [
            text for text in required_route_text
            if text not in route_output
        ]
        if missing_route_text:
            raise ReleaseCheckError(
                "installed adopted-lockout route omitted: "
                + ", ".join(missing_route_text)
            )
        if (adopted / ".writwall-bootstrap").exists():
            raise ReleaseCheckError(
                "installed adopted-lockout route published a bootstrap"
            )
        if tree_digest(adopted) != adopted_before:
            raise ReleaseCheckError(
                "installed adopted-lockout route changed target bytes"
            )

        retired = workspace / "retired-project"
        retired_governance = retired / "governance"
        retired_decisions = retired_governance / "decisions"
        retired_decisions.mkdir(parents=True)
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (retired_governance / name).write_text(
                f"# {name}\n", encoding="utf-8", newline="\n"
            )
        (retired_decisions / "DR-001.md").write_text(
            RATIFIED_ADOPTION_RECORD, encoding="utf-8", newline="\n"
        )
        (retired_governance / "history").mkdir()
        (retired_governance / "history" / "WO-001.md").write_text(
            "---\nid: WO-001\nstatus: CLOSED\n---\n", encoding="utf-8", newline="\n"
        )
        retired_before = tree_digest(retired)
        retired_result = run(
            [str(command), "start", "--project-root", str(retired)],
            cwd=workspace,
            environment=environment,
            label="installed retired-lockout route",
        )
        if "Observed lifecycle state: retired_lockout" not in retired_result.stdout:
            raise ReleaseCheckError(
                "installed retired-lockout route omitted the expected lifecycle state"
            )
        if tree_digest(retired) != retired_before:
            raise ReleaseCheckError(
                "installed retired-lockout route changed target bytes"
            )

        draft = workspace / "draft-unratified-project"
        draft_governance = draft / "governance"
        draft_decisions = draft_governance / "decisions"
        draft_decisions.mkdir(parents=True)
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (draft_governance / name).write_text(
                f"# {name}\n", encoding="utf-8", newline="\n"
            )
        (draft_decisions / "DR-001.md").write_text(
            DRAFT_ADOPTION_RECORD, encoding="utf-8", newline="\n"
        )
        (draft_decisions / "DR-999-unrelated.md").write_text(
            UNRELATED_RATIFIED_DECISION, encoding="utf-8", newline="\n"
        )
        (draft_governance / "history").mkdir()
        (draft_governance / "history" / "WO-001.md").write_text(
            "---\nid: WO-001\nstatus: CLOSED\n---\n", encoding="utf-8", newline="\n"
        )
        draft_before = tree_digest(draft)
        draft_result = run(
            [str(command), "start", "--project-root", str(draft)],
            cwd=workspace,
            environment=environment,
            label="installed draft-adoption-record regression route",
        )
        if "Observed lifecycle state: adopted_lockout" in draft_result.stdout:
            raise ReleaseCheckError(
                "installed draft-adoption-record regression reported adopted_lockout"
            )
        if "Observed lifecycle state: retired_lockout" in draft_result.stdout:
            raise ReleaseCheckError(
                "installed draft-adoption-record regression reported retired_lockout"
            )
        if tree_digest(draft) != draft_before:
            raise ReleaseCheckError(
                "installed draft-adoption-record regression changed target bytes"
            )

        unrelated = workspace / "unrelated-signed-decision-project"
        unrelated_governance = unrelated / "governance"
        unrelated_decisions = unrelated_governance / "decisions"
        unrelated_decisions.mkdir(parents=True)
        for name in ("PLAN.md", "STATE.md", "ROUTING.md"):
            (unrelated_governance / name).write_text(
                f"# {name}\n", encoding="utf-8", newline="\n"
            )
        (unrelated_decisions / "DR-001.md").write_text(
            UNRELATED_RATIFIED_DECISION, encoding="utf-8", newline="\n"
        )
        unrelated_before = tree_digest(unrelated)
        unrelated_result = subprocess.run(
            [str(command), "start", "--project-root", str(unrelated)],
            cwd=workspace,
            env=environment,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if unrelated_result.returncode == 0:
            raise ReleaseCheckError(
                "installed coordinator did not fail closed for a signed but "
                "unrelated document at the exact adoption-record path"
            )
        unrelated_output = unrelated_result.stdout + unrelated_result.stderr
        if "adopted_lockout" in unrelated_output or "retired_lockout" in unrelated_output:
            raise ReleaseCheckError(
                "installed coordinator reported a lockout state for a signed "
                "but unrelated document at the exact adoption-record path"
            )
        if tree_digest(unrelated) != unrelated_before:
            raise ReleaseCheckError(
                "installed unrelated-signed-decision regression changed target bytes"
            )

        worktree_root = workspace / "worktree-project"
        worktree_root.mkdir()
        (worktree_root / ".git").mkdir()
        nested = worktree_root / "nested" / "workspace"
        nested.mkdir(parents=True)
        worktree_before = tree_digest(worktree_root)
        worktree_result = subprocess.run(
            [str(command), "start", "--project-root", str(nested)],
            cwd=workspace,
            env=environment,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if worktree_result.returncode == 0:
            raise ReleaseCheckError(
                "installed coordinator did not stop for a directory nested "
                "inside a Git worktree"
            )
        worktree_output = worktree_result.stdout + worktree_result.stderr
        if "worktree" not in worktree_output.lower():
            raise ReleaseCheckError(
                "installed coordinator's nested-worktree stop omitted a "
                "worktree diagnostic"
            )
        if (nested / ".writwall-bootstrap").exists():
            raise ReleaseCheckError(
                "installed coordinator's nested-worktree stop published a bootstrap"
            )
        if tree_digest(worktree_root) != worktree_before:
            raise ReleaseCheckError(
                "installed coordinator's nested-worktree stop changed target bytes"
            )

    verify_candidate_unchanged(candidate, before)

    print("OK: coordinator release candidate passed")
    print(f"  installed version : {expected_version}")
    print("  installed command : help and real start passed under normal bytecode behavior")
    print("  conversation-first: bare installed start produced the Architect handoff")
    print("  complete handoff  : all required packets present; no bytecode residue")
    print("  canonical root    : installed coordinator recorded the resolved project root")
    print("  adopted lockout   : fresh General route; zero target-byte change")
    print("  retired lockout   : ratified adoption plus closed history; zero target-byte change")
    print("  draft regression  : draft adoption record never reports adopted/retired lockout")
    print("  unrelated regression: signed unrelated document at the exact adoption-record")
    print("                      path fails closed; zero target-byte change")
    print("  nested worktree   : installed coordinator stops with a worktree diagnostic")
    print("  candidate unchanged: complete-tree digest preserved")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description=(
            "Build, install, and smoke-test Writwall from an external public "
            "release candidate without modifying candidate bytes."
        )
    )
    value.add_argument("candidate", type=Path)
    value.add_argument(
        "--expected-tag",
        required=True,
        help="canonical release tag that must match candidate package metadata",
    )
    return value


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        check_candidate(arguments.candidate, arguments.expected_tag)
    except (OSError, ReleaseCheckError, subprocess.SubprocessError) as exc:
        print(f"FAIL: coordinator release candidate: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
