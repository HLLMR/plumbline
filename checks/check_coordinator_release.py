# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Install and smoke-test Writwall from an external release candidate."""

from __future__ import annotations

import argparse
import hashlib
import os
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
    "OWNER-AGENT.md",
    "REPOSITORY-OPERATOR.md",
    "REVIEWER.md",
    "NAME-CLEARANCE.md",
    "OWNER-RATIFICATION.md",
    "writwall-adopt/SKILL.md",
    "writwall-adopt/assets/scripts/collect_name_clearance.py",
    "writwall-adopt/assets/checks/check_name_clearance.py",
    "writwall-adopt/references/name-clearance.md",
)


class ReleaseCheckError(RuntimeError):
    """A bounded, user-facing release-candidate failure."""


def tree_digest(root: Path) -> str:
    lines: list[str] = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {relative}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def run(command: list[str], *, cwd: Path, environment: dict[str, str],
        label: str, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
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


def check_candidate(candidate: Path) -> None:
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

    verify_candidate_unchanged(candidate, before)

    print("OK: coordinator release candidate passed")
    print(f"  installed version : {expected_version}")
    print("  installed command : help and real start passed under normal bytecode behavior")
    print("  complete handoff  : all required packets present; no bytecode residue")
    print("  candidate unchanged: complete-tree digest preserved")


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(
        description=(
            "Build, install, and smoke-test Writwall from an external public "
            "release candidate without modifying candidate bytes."
        )
    )
    value.add_argument("candidate", type=Path)
    return value


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        check_candidate(arguments.candidate)
    except (OSError, ReleaseCheckError, subprocess.SubprocessError) as exc:
        print(f"FAIL: coordinator release candidate: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
