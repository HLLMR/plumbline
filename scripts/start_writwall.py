# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Create a local-first Writwall bootstrap handoff without adopting a project."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1]
BUNDLE_SOURCE = SOURCE_ROOT / "skills" / "writwall-adopt"
OUTPUT_NAME = ".writwall-bootstrap"
SECRET_WARNING = (
    "Do not enter passwords, API tokens, private keys, mail contents, DNS "
    "record values, or other secrets. This tool writes your answers as plain "
    "text inside the target project."
)

DNS_MAIL_SCENARIO = (
    "DNS provider selection",
    "DNS inventory and cutover",
    "mail routing cutover",
    "mailbox data migration",
    "repository and website work",
)
DNS_MAIL_SCENARIO_CONTEXT = (
    "Move authoritative DNS for eight domains first; only after verified DNS "
    "authority cutover, change mail routing; separately inventory, clean, and "
    "migrate historical mailbox data."
)
WINDOWS_RESERVED_STEMS = frozenset({
    "con", "prn", "aux", "nul", "clock$",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
})


class CoordinatorError(RuntimeError):
    """A safe, user-facing stop before the published output exists."""


@dataclass(frozen=True)
class ObservedState:
    name: str
    evidence: tuple[str, ...]
    active_work_order: str | None = None


def _is_linklike(path: Path) -> bool:
    """Return true for symlinks and Windows junction/reparse entries."""
    try:
        if path.is_symlink():
            return True
        isjunction = getattr(os.path, "isjunction", None)
        if isjunction and isjunction(path):
            return True
        try:
            attributes = path.lstat().st_file_attributes
        except FileNotFoundError:
            return False
        except AttributeError:
            return False
        return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except OSError:
        return True


def _entry_exists(path: Path) -> bool:
    """Unlike Path.exists(), include dangling symlinks and reparse entries."""
    try:
        return os.path.lexists(path)
    except OSError:
        return True


def _safe_project_path(project: Path, path: Path, label: str) -> Path:
    """Reject linklike components and containment escapes before any read."""
    try:
        relative = path.relative_to(project)
    except ValueError as exc:
        raise CoordinatorError(f"inconsistent state: {label} is outside the project") from exc
    current = project
    for part in relative.parts:
        current = current / part
        if _is_linklike(current):
            raise CoordinatorError(
                f"inconsistent state: {label} contains a symlink, junction, or reparse entry"
            )
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise CoordinatorError(f"inconsistent state: {label} is unreadable: {exc}") from exc
    if resolved != project and project not in resolved.parents:
        raise CoordinatorError(f"inconsistent state: {label} resolves outside the project")
    return resolved


def frontmatter_status(path: Path) -> str | None:
    """Read only an exact top-level status scalar from opening frontmatter."""
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as exc:
        raise CoordinatorError(f"cannot read pointed work order: {exc}") from exc
    if not lines or lines[0] != "---":
        return None
    for line in lines[1:]:
        if line == "---":
            break
        if line.startswith((" ", "\t")):
            continue
        match = re.fullmatch(r"status:\s*(['\"]?)([^'\"#]+)\1\s*(?:#.*)?", line)
        if match:
            return match.group(2).strip()
    return None


def _safe_pointer_target(project: Path, value: str) -> Path:
    raw = value.strip().replace("\\", "/")
    if not raw or "\n" in raw or "\r" in raw:
        raise CoordinatorError("inconsistent state: activation pointer is empty or multiline")
    parts = tuple(part for part in raw.split("/") if part)
    if parts[:2] != ("governance", "work-orders") or any(
        part in (".", "..") for part in parts
    ):
        raise CoordinatorError(
            "inconsistent state: activation pointer is not a repository-relative "
            "governance/work-orders path"
        )
    target = project.joinpath(*parts)
    resolved_target = _safe_project_path(
        project, target, "activation pointer target"
    )
    work_orders = _safe_project_path(
        project, project / "governance" / "work-orders", "work-order directory"
    )
    if work_orders not in resolved_target.parents or not resolved_target.is_file():
        raise CoordinatorError(
            "inconsistent state: activation pointer target is outside the work-order "
            "directory or not a regular file"
        )
    return resolved_target


def classify_project(project: Path) -> ObservedState:
    """Classify lifecycle state from repository bytes, never chat context."""
    claude_dir = project / ".claude"
    if _entry_exists(claude_dir):
        resolved_claude = _safe_project_path(project, claude_dir, ".claude directory")
        if not resolved_claude.is_dir():
            raise CoordinatorError("inconsistent state: .claude is not a directory")
    pointer = claude_dir / "active-wo.txt"
    pointer_siblings = tuple(
        path for path in claude_dir.glob("active-wo.*")
        if path.name != "active-wo.txt"
    ) if claude_dir.is_dir() else ()
    if pointer_siblings:
        for sibling in pointer_siblings:
            _safe_project_path(project, sibling, "possible activation pointer")
        names = ", ".join(sorted(path.name for path in pointer_siblings))
        raise CoordinatorError(
            f"inconsistent state: possible misnamed activation pointer(s): {names}"
        )

    pointed_target: Path | None = None
    if _entry_exists(pointer):
        resolved_pointer = _safe_project_path(project, pointer, "activation pointer")
        if not resolved_pointer.is_file():
            raise CoordinatorError("inconsistent state: activation pointer is not a regular file")
        try:
            pointer_value = pointer.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            raise CoordinatorError(
                f"inconsistent state: activation pointer is unreadable: {exc}"
            ) from exc
        pointed_target = _safe_pointer_target(project, pointer_value)
        status = frontmatter_status(pointed_target)
        if status != "ACTIVE":
            raise CoordinatorError(
                "inconsistent state: activation pointer resolves, but the work order "
                f"status is {status!r}, not 'ACTIVE'"
            )
    live_orders = project / "governance" / "work-orders"
    active_orders: list[Path] = []
    if _entry_exists(live_orders):
        resolved_orders = _safe_project_path(
            project, live_orders, "work-order directory"
        )
        if not resolved_orders.is_dir():
            raise CoordinatorError("inconsistent state: work-order path is not a directory")
        for path in live_orders.glob("*.md"):
            safe_path = _safe_project_path(project, path, "work-order record")
            if not safe_path.is_file():
                raise CoordinatorError("inconsistent state: work-order record is not a file")
            if frontmatter_status(safe_path) == "ACTIVE":
                active_orders.append(safe_path)

    if pointed_target is not None:
        extras = [path for path in active_orders if path != pointed_target]
        if extras or pointed_target not in active_orders:
            names = ", ".join(sorted(path.name for path in active_orders)) or "none"
            raise CoordinatorError(
                "inconsistent state: activation pointer does not identify the only ACTIVE "
                f"work order; observed ACTIVE records: {names}"
            )
        relative = pointed_target.relative_to(project).as_posix()
        return ObservedState(
            "active_work_order",
            ("activation pointer exists", f"pointed work order is ACTIVE: {relative}"),
            relative,
        )

    if active_orders:
        names = ", ".join(sorted(path.name for path in active_orders))
        raise CoordinatorError(
            "inconsistent state: ACTIVE work order(s) exist without an activation "
            f"pointer: {names}"
        )

    governance = project / "governance"
    if _entry_exists(governance):
        resolved_governance = _safe_project_path(
            project, governance, "governance directory"
        )
        if not resolved_governance.is_dir():
            raise CoordinatorError("inconsistent state: governance is not a directory")
    core = tuple(governance / name for name in ("PLAN.md", "STATE.md", "ROUTING.md"))
    adoption_records = (
        governance / "decisions" / "DR-001.md",
        governance / "ADOPTION-RECORD.md",
    )
    history = governance / "history"
    closed_records = []
    if _entry_exists(history):
        resolved_history = _safe_project_path(project, history, "history directory")
        if not resolved_history.is_dir():
            raise CoordinatorError("inconsistent state: history is not a directory")
        for path in history.glob("WO-*.md"):
            safe_path = _safe_project_path(project, path, "historical work-order record")
            if not safe_path.is_file():
                raise CoordinatorError(
                    "inconsistent state: historical work-order record is not a file"
                )
            if frontmatter_status(safe_path) in {"CLOSED", "COMPLETE"}:
                closed_records.append(safe_path)

    for path in (*core, *adoption_records):
        if _entry_exists(path):
            resolved = _safe_project_path(project, path, "governance control file")
            if not resolved.is_file():
                raise CoordinatorError(
                    "inconsistent state: governance control path is not a file"
                )

    if all(path.is_file() for path in core) and closed_records:
        return ObservedState(
            "retired_lockout",
            (
                "activation pointer is absent",
                "Plan, State, and Routing exist",
                f"{len(closed_records)} closed work-order record(s) observed in history",
            ),
        )
    if all(path.is_file() for path in core) and any(
        path.is_file() for path in adoption_records
    ):
        return ObservedState(
            "adopted_lockout",
            (
                "activation pointer is absent",
                "Plan, State, Routing, and an adoption record exist",
            ),
        )

    writwall_markers = (
        project / ".claude" / "hooks" / "wo_capability_wall.py",
        project / ".claude" / "settings.json",
        governance / "PLAN.md",
        governance / "STATE.md",
        governance / "ROUTING.md",
        project / "START-HERE.md",
        project / "ADOPTING.md",
    )
    found_items = []
    for path in writwall_markers:
        if _entry_exists(path):
            _safe_project_path(project, path, "Writwall marker")
            found_items.append(path.relative_to(project).as_posix())
    found = tuple(found_items)
    if found:
        return ObservedState(
            "partial_bootstrap",
            ("activation pointer is absent", "Writwall-shaped material exists: " + ", ".join(found)),
        )
    return ObservedState(
        "clean_new",
        ("activation pointer is absent", "no Writwall control-plane or governance markers found"),
    )


def portable_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise CoordinatorError(f"external Operator function {value!r} has no portable name")
    slug = slug[:80].rstrip("-")
    if slug in WINDOWS_RESERVED_STEMS:
        slug = f"operator-{slug}"
    return slug


def operation_packet(function_name: str) -> str:
    return f"""# External operations packet: {function_name}

This scaffold is inert. It confers no authority to access or mutate any system.
The Owner-Agent fills it from ratified intent; the named Operator executes only
the completed packet and returns evidence.

## Preconditions

- [ ] Identify the exact system, account boundary, and observed baseline.
- [ ] Name a stop condition for unexpected state.

## Permitted actions

- [ ] List exact authorized actions; an empty list authorizes nothing.

## Prohibited actions

- No repository-byte edits unless a separate repository work order grants them.
- No credential disclosure, persistence, or transmission through this packet.
- No adjacent-system change merely because it is convenient.

## Verification

- [ ] State exact observations and pass conditions.

## Rollback

- [ ] State the last safe point and exact restoration procedure.

## Evidence to return

- [ ] Return timestamps, sanitized before/after observations, and command or UI results.
- Never return credentials, private keys, mailbox content, or secret record values.

## Credential boundary

Credentials remain in the Operator's approved secret store or interactive
provider session. The Owner may authenticate when unavoidable; authentication
does not transfer decision authority. This external Operator remains outside
the repository capability wall unless it edits repository bytes.
"""


def role_split_recommendation(functions: tuple[str, ...]) -> str:
    external = (
        f" Add {len(functions)} separately bounded external function packet(s); "
        "the Owner may assign multiple packets to one Operator only when the "
        "same account boundary, verification, and rollback apply."
        if functions else
        " Add no external Operator unless the project later names an external system."
    )
    return (
        "Use one human Owner, one Owner-Agent coordinator, one repository "
        "Operator when repository mutation begins, and one fresh Reviewer."
        + external
    )


def next_prompt(state: ObservedState) -> tuple[str, str]:
    if state.name == "clean_new":
        return (
            "Adoption coordinator before wall registration",
            """Act as my Writwall adoption coordinator, not as an Implementer. Read
`.writwall-bootstrap/writwall-adopt/SKILL.md` and use bootstrap mode. Treat
`.writwall-bootstrap/intake.json` as unratified intake, not authority. I decide
and ratify; perform every clerical step an authorized recorder may perform.
Ask one question at a time in plain language, recommendation first. Do not
install or register the wall until the complete bundle and recovery instructions
are locally readable. Do not begin product work or WO-001 before adoption.""",
        )
    if state.name == "partial_bootstrap":
        return (
            "External recovery coordinator",
            """Act as my Writwall accidental-overlay or incomplete-adoption recovery coordinator,
not as an Implementer. Read `.writwall-bootstrap/writwall-adopt/SKILL.md`.
Inventory only; do not delete, overwrite, move, install, register, activate, or
invent missing intent. Use the observed-state evidence in the handoff, propose
an exact disposition packet, and ask one question at a time.""",
        )
    if state.name in {"adopted_lockout", "retired_lockout"}:
        return (
            "Dispatcher for a new candidate work order",
            """Act as Dispatcher. The repository is in observed lockout; no active work order
is established. Read the charter, Plan, State, Routing, and ratified adoption
record. Draft one bounded work order for the project's genuine next task.
Generate and validate its boundaries, but do not activate it. Return the exact
candidate and scope rationale for Owner approval.""",
        )
    if state.name == "active_work_order":
        return (
            "Walled repository Implementer",
            """Act as Implementer for the active work order only. Re-read the activation
pointer and pointed work order from repository bytes, confirm the active
dispatch and required live-wall canary before mutation, execute only its grant,
write its report, and stop before acceptance or closeout.""",
        )
    raise CoordinatorError(f"inconsistent state: unsupported classification {state.name!r}")


def render_time(owner_time: str) -> str:
    if owner_time == "yes":
        return """**Owner active-minute capture: ENABLED.** Start when the first intake
question is presented. Stop when the coordinator returns the ratifiable adoption
packet or next-work-order candidate. Human reading, deciding, responding,
authentication, and unavoidable UI work count. Agent execution and waiting do
not. Report the actual total at acceptance; never reconstruct it later."""
    return """**Owner active minutes: NOT REPORTED.** Capture was declined for this
bootstrap. Do not infer or reconstruct a value."""


def render_handoff(args: argparse.Namespace, state: ObservedState,
                   functions: tuple[str, ...]) -> str:
    role, prompt = next_prompt(state)
    evidence = "\n".join(f"- {item}" for item in state.evidence)
    operator_rows = "\n".join(
        f"- **{name}:** give `operations/{portable_slug(name)}.md` to the agent "
        "or administrator that can reach only that external function."
        for name in functions
    ) or "- No external Operator function was named during intake."
    active = (
        f"\nPointed work order: `{state.active_work_order}`."
        if state.active_work_order else ""
    )
    scenario = (
        "\n## Scenario boundary\n\n"
        f"{DNS_MAIL_SCENARIO_CONTEXT}\n"
        if args.scenario == "dns-mail-migration" else ""
    )
    return f"""# Writwall day-zero handoff: {args.project_name}

This directory is temporary bootstrap material. It does not install or adopt
Writwall, ratify intent, activate a work order, or grant external authority.
Remove it before the adoption commit after the authorized recorder no longer
needs it.

{SECRET_WARNING}

## Observed lifecycle state

**{state.name}**{active}

{evidence}

Repository bytes, not prior chat, determine this state. Re-run the coordinator
if those bytes change before acting.

## Project intake

- Project: {args.project_name}
- Purpose: {args.purpose}
- Preferred primary agent/interface: {args.agent}
- Execution location: {args.location}
- Repository and external environment: {args.environment}

These answers are unratified intake. The Owner must approve material intent.
{scenario}
## Recommended smallest credible role split

{role_split_recommendation(functions)}

## Who to open next

**{role}**, using **{args.agent}** at **{args.location}**.

Paste exactly:

```text
{prompt}
```

## Authority and mechanics

- The human Owner decides intent, identity, risk acceptance, lifecycle actions,
  provider selection, production cutovers, and acceptance.
- The Owner-Agent may interview, draft, route, record exact ratified decisions,
  and perform explicitly authorized clerical lifecycle mechanics.
- A repository Operator works only under the active work order.
- A fresh Reviewer evaluates the order, result, evidence, and report without
  implementing corrections in the same context.
- External Operators receive only bounded packets. The Owner-Agent retains the
  proverbial keys: routing and authority, not passwords or cryptographic keys.

## External Operator routing

{operator_rows}

Provider selection, DNS authority, mail routing, mailbox data, repository work,
and deployment are separate decision or execution boundaries. Do not collapse
them into one broad infrastructure authorization.

## Owner-time measurement

{render_time(args.owner_time)}
"""


def write_bootstrap(project: Path, args: argparse.Namespace, state: ObservedState,
                    functions: tuple[str, ...]) -> Path:
    output = project / OUTPUT_NAME
    if _entry_exists(output):
        raise CoordinatorError(
            f"create-only stop: {OUTPUT_NAME} already exists; nothing was overwritten"
        )
    if _is_linklike(BUNDLE_SOURCE) or not BUNDLE_SOURCE.is_dir():
        raise CoordinatorError("Writwall adoption bundle is missing from this distribution")
    bundle_files = sorted(path for path in BUNDLE_SOURCE.rglob("*") if path.is_file())
    if not bundle_files:
        raise CoordinatorError("Writwall adoption bundle is empty")
    for source in bundle_files:
        current = BUNDLE_SOURCE
        for part in source.relative_to(BUNDLE_SOURCE).parts:
            current = current / part
            if _is_linklike(current):
                raise CoordinatorError(
                    "Writwall adoption bundle contains a symlink, junction, or reparse entry"
                )

    slugs = [portable_slug(name) for name in functions]
    if len(slugs) != len(set(slugs)):
        raise CoordinatorError("external Operator names collapse to duplicate portable filenames")

    stage = project.parent / (
        f".{project.name}-writwall-bootstrap-stage-{uuid.uuid4().hex}"
    )
    try:
        stage.mkdir()
    except OSError as exc:
        raise CoordinatorError(
            f"cannot create same-filesystem bootstrap stage outside the target: {exc}"
        ) from exc
    try:
        bundle_target = stage / "writwall-adopt"
        for source in bundle_files:
            relative = source.relative_to(BUNDLE_SOURCE)
            target = bundle_target / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())

        intake = {
            "schema": 1,
            "observed_state": state.name,
            "state_evidence": list(state.evidence),
            "active_work_order": state.active_work_order,
            "project_name": args.project_name,
            "purpose": args.purpose,
            "preferred_agent": args.agent,
            "execution_location": args.location,
            "repository_external_environment": args.environment,
            "scenario": args.scenario,
            "scenario_context": (
                DNS_MAIL_SCENARIO_CONTEXT
                if args.scenario == "dns-mail-migration" else None
            ),
            "recommended_role_split": role_split_recommendation(functions),
            "external_operator_functions": list(functions),
            "owner_time_capture": args.owner_time == "yes",
            "project_root": ".",
            "authority": "unratified_intake_only",
        }
        (stage / "intake.json").write_text(
            json.dumps(intake, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        (stage / "HANDOFF.md").write_text(
            render_handoff(args, state, functions),
            encoding="utf-8",
            newline="\n",
        )
        if functions:
            operations = stage / "operations"
            operations.mkdir()
            for name, slug in zip(functions, slugs):
                (operations / f"{slug}.md").write_text(
                    operation_packet(name), encoding="utf-8", newline="\n"
                )
        if _entry_exists(output):
            raise CoordinatorError(
                f"create-only stop: {OUTPUT_NAME} appeared during creation; nothing was overwritten"
            )
        os.rename(stage, output)
    except Exception as exc:
        cleanup_error = None
        if _entry_exists(stage):
            try:
                shutil.rmtree(stage)
            except OSError as cleanup_exc:
                cleanup_error = cleanup_exc
        if _entry_exists(stage):
            raise CoordinatorError(
                "bootstrap publication failed and the complete external stage "
                f"could not be removed: {stage} ({cleanup_error})"
            ) from exc
        raise CoordinatorError(
            f"bootstrap creation stopped before atomic publication; no target "
            f"output was created: {exc}"
        ) from exc
    return output


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{prompt}{suffix}: ").strip()
    return answer or (default or "")


def interactive_args(args: argparse.Namespace) -> argparse.Namespace:
    print(SECRET_WARNING)
    if not args.owner_time:
        args.owner_time = ask(
            "Track Owner active minutes? If yes, start a timer before answering",
            "yes",
        ).lower()
    if args.owner_time == "yes":
        print(
            "Owner timer starts now: count your reading, decisions, responses, "
            "authentication, and unavoidable UI work; exclude agent waiting."
        )
    confirmation = ask("Continue without entering secrets?", "yes").lower()
    if confirmation not in {"y", "yes"}:
        raise CoordinatorError("stopped before reading project intake")
    args.confirm_no_secrets = True
    args.project_root = args.project_root or ask("Target project directory", ".")
    args.project_name = args.project_name or ask("Project name")
    if not args.brief_file and not args.purpose:
        supplied_brief = ask("Existing project brief file path, or blank", "")
        if supplied_brief:
            args.brief_file = supplied_brief
    if args.brief_file:
        args.purpose = ""
    else:
        args.purpose = args.purpose or ask("Explain the project purpose in your own words")
    args.agent = args.agent or ask(
        "Preferred primary agent and interface", "Claude Code in VS Code"
    )
    args.location = args.location or ask(
        "Where will that agent run?", "local project workspace"
    )
    args.environment = args.environment or ask(
        "Describe the repository and any external environment it must coordinate with",
        "local repository only",
    )
    print(
        "Recommended minimum: one Owner-Agent, one repository Operator when "
        "mutation starts, one fresh Reviewer, and external Operators only for "
        "distinct account or rollback boundaries."
    )
    if not args.external_operator and not args.scenario:
        external = ask(
            "External Operator functions, comma-separated (DNS, mail, VPS), or blank",
            "",
        )
        args.external_operator = [part.strip() for part in external.split(",") if part.strip()]
    return args


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare a create-only, project-local Writwall adoption handoff. "
            "This does not install or adopt Writwall."
        )
    )
    parser.add_argument("--project-root")
    parser.add_argument("--project-name")
    parser.add_argument("--purpose")
    parser.add_argument("--brief-file")
    parser.add_argument("--agent")
    parser.add_argument("--location")
    parser.add_argument("--environment")
    parser.add_argument("--external-operator", action="append", default=[])
    parser.add_argument("--scenario", choices=("dns-mail-migration",))
    parser.add_argument("--owner-time", choices=("yes", "no"))
    parser.add_argument("--confirm-no-secrets", action="store_true")
    parser.add_argument("--non-interactive", action="store_true")
    return parser.parse_args(argv)


def normalize_args(args: argparse.Namespace) -> tuple[argparse.Namespace, Path, tuple[str, ...]]:
    if not args.non_interactive:
        args = interactive_args(args)
    required = {
        "project root": args.project_root,
        "project name": args.project_name,
        "primary agent/interface": args.agent,
        "execution location": args.location,
        "repository/external environment": args.environment,
        "Owner-time choice": args.owner_time,
    }
    missing = [name for name, value in required.items() if not value]
    if args.non_interactive and not args.confirm_no_secrets:
        raise CoordinatorError(
            "non-interactive use requires --confirm-no-secrets; secrets must not be supplied"
        )
    if missing:
        raise CoordinatorError("missing required intake: " + ", ".join(missing))

    supplied_project = Path(args.project_root).expanduser()
    if supplied_project.is_symlink():
        raise CoordinatorError("target project must not be a symlink")
    try:
        project = supplied_project.resolve(strict=True)
    except OSError as exc:
        raise CoordinatorError(f"target project directory is not readable: {exc}") from exc
    if not project.is_dir() or project.is_symlink():
        raise CoordinatorError("target project must be an existing, non-symlink directory")

    if args.brief_file:
        brief = Path(args.brief_file).expanduser()
        try:
            purpose = brief.read_text(encoding="utf-8-sig").strip()
        except (OSError, UnicodeError) as exc:
            raise CoordinatorError(f"cannot read supplied brief: {exc}") from exc
        if not purpose:
            raise CoordinatorError("supplied brief is empty")
        args.purpose = purpose
    if not args.purpose:
        raise CoordinatorError("missing project purpose or --brief-file")

    functions = list(args.external_operator)
    if args.scenario == "dns-mail-migration":
        functions.extend(name for name in DNS_MAIL_SCENARIO if name not in functions)
    normalized = tuple(name.strip() for name in functions if name.strip())
    return args, project, normalized


def main(argv: list[str] | None = None) -> int:
    try:
        args, project, functions = normalize_args(parse_args(argv))
        if _entry_exists(project / OUTPUT_NAME):
            raise CoordinatorError(
                f"create-only stop: {OUTPUT_NAME} already exists; nothing was overwritten"
            )
        state = classify_project(project)
        output = write_bootstrap(project, args, state, functions)
    except CoordinatorError as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        return 2
    print(f"Observed lifecycle state: {state.name}")
    print(f"Created: {output.as_posix()}")
    print(f"Next: read {(output / 'HANDOFF.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
