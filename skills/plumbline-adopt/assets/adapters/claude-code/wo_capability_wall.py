#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: MIT-0
"""Standalone PreToolUse capability wall for Doctrine rev 0.8.

Standard library only. Install as a single standalone file; it imports nothing
from this repository.

Register with matcher "*". This hook classifies tools itself rather than
relying on a matcher expression, so that a tool introduced by a later version
of the provider is denied until someone classifies it, instead of silently
becoming an unwalled mutation channel (8.3.3).

WHAT THIS ADAPTER MAKES PHYSICAL
  1. No-work-order lockout (8.3.5.1). With no valid active work order, every
     modeled mutation-capable tool is denied. A pointed record must contain
     exactly one top-level status: ACTIVE before any mutation may proceed.
  2. grant.filesystem.write for FILE_EDIT_TOOLS. Narrow repository-relative
     paths are resolved component-wise; repository-root, escape, parent-
     traversal, symlink, junction, and target-alias widening are rejected.
  3. The Doctrine 8.7 protected-control-plane floor for every file-edit tool.
     Pointer, installed hook, installed settings, active record, and denial
     log mutation is denied regardless of the grant. Shell tools are denied
     even under restricted/allowed because they expose no exact target from
     which the wall could prove that protected artifacts remain unchanged.
     Unsupported mutation, delegation, MCP, and unknown tools remain denied.
     The mechanism's own private log_denial() append is not grant authority.
  4. grant.filesystem.read.deny for the tools in READ_TOOLS (Read, Glob,
     Grep, LS, NotebookRead), only while a valid active work order declares
     it. An exact-file read inside a denied path, or below a recursive
     denied path, is denied; a traversal/search tool is denied when its
     resolved root lies inside a denied subtree or is an ancestor whose
     traversal could reach one, including an omitted root (repository
     root). No-work-order lockout does not apply to READ_TOOLS: an absent
     pointer leaves ordinary review available. Once a pointer exists, unsafe
     pointer or unreadable/malformed work-order state fails closed for modeled
     reads with a stage-specific reason.
  5. network.egress for WebFetch and WebSearch. Denied, absent, or invalid
     authority blocks them; only the exact supported value allowed passes.
  6. Fail closed on anything indeterminate: unreadable or unsafe work-order
     pointer, malformed frontmatter, non-ACTIVE lifecycle, missing grant,
     invalid shell/network value, unsupported grant path syntax, an edit call whose target cannot
     be determined, a malformed grant.filesystem.read.deny entry, or a read
     call whose target cannot be determined or resolved inside the
     repository.
  7. Fail closed on tools this adapter does not model, including every
     mcp__* tool and any tool name it does not recognize.

WHAT THIS ADAPTER DOES NOT YET CLAIM AS A WHOLE ENFORCED SURFACE
  - Any of the eight minimum grant surfaces. Logic coverage is channel-local;
    the strict 8.3.3 metric stays unchanged until fresh installed birth tests
    inventory every provider channel. During WO-PL-026 the honest state is
    declared 8 / enforced 0 / unenforced 8.
  - Filesystem read denial beyond the named READ_TOOLS. Shell is categorically
    denied rather than parsed, but provider startup failure remains outside
    the hook's control.
  - network.egress beyond WebFetch and WebSearch. MCP and unknown tools deny;
    no complete provider inventory has yet qualified the whole surface.
  - package.install, secrets.read, git.commit, git.push as whole surfaces.
  - Doctrine 8.7 enforcement in an installed provider. The source logic is
    present, but the claim remains pending exact installation and native
    Windows/POSIX birth tests.
  - Its own launch. A command hook that cannot start, or that times out, does
    not block the tool call in current Claude Code. See README.md, "Provider
    limitation". This adapter can fail closed only for errors it catches.

Active WO pointer: <repo>/.claude/active-wo.txt, holding a repository-relative
path inside governance/work-orders/.

DENIAL EVIDENCE
Denials append one JSON object per line to <repo>/governance/LOG-denials.jsonl,
LF-terminated on every platform. Field names are stable and are documented in
README.md, "Denial log". The record carries only evidence-safe fields:

  schema       integer schema version
  timestamp    UTC RFC 3339, second precision
  session_id   provider session identifier, or null when not supplied
  tool         tool name as received, or null when unusable
  surface      classified surface/channel
  work_order   repository-relative active-work-order path, or null
  decision     always "deny"
  reason_code  stable machine-readable code
  reason       concise human-readable sentence

The logged reason is deliberately NOT the full reason returned to the provider.
Tool arguments, prompts, file contents, environment variables, usernames, drive
letters, absolute paths, tokens, and secrets are never written to the log. The
provider-facing reason may name a rejected path so the agent can act on it; the
log carries the reason code instead.

A logging failure never opens the wall. The deny decision is emitted whether or
not the record could be written.

Run ``--preflight`` for a read-only installation check. It supports CPython
3.10 through 3.14, verifies native Windows/POSIX interpreter commands,
project-root placement, exact installed digest, project matcher/source,
portable registration, and explicit timeout, and never appends evidence.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import stat
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Tool classification. Version-specific by nature: re-inventory at every birth
# test (8.3.5) and after any provider upgrade. Unknown names deny.
# --------------------------------------------------------------------------

# Governed by grant.filesystem.write. MultiEdit is retained only as
# backwards-compatible coverage for installations that still expose it.
FILE_EDIT_TOOLS = frozenset({
    "Edit",
    "MultiEdit",
    "NotebookEdit",
    "Write",
})

# Governed by grant.shell.execute.
SHELL_TOOLS = frozenset({
    "Bash",
    "KillShell",
    "Monitor",
    "PowerShell",
})

# Filesystem-reading provider tools this adapter can model well enough to
# apply grant.filesystem.read.deny to. Governed by that grant field.
READ_TOOLS = frozenset({
    "Glob",
    "Grep",
    "LS",
    "NotebookRead",
    "Read",
})

# Filesystem-reading tools that name one exact file/notebook to open, and the
# tool_input key naming that target.
EXACT_READ_TOOL_KEYS = {
    "NotebookRead": "notebook_path",
    "Read": "file_path",
}

# Filesystem-reading tools that traverse or search from an optional root.
# Omitted root means repository root (Doctrine 8.3.5, B.3.3.8).
TRAVERSAL_READ_TOOLS = frozenset({"Glob", "Grep", "LS"})

# Inspection and session-control tools that expose no modeled mutation surface.
# Some may return provider metadata; this classification makes no read-secrecy
# claim. They pass through to normal Claude Code permission evaluation.
NONMUTATING_TOOLS = frozenset({
    "AskUserQuestion",
    "BashOutput",
    "CronList",
    "EnterPlanMode",
    "ExitPlanMode",
    "ListMcpResourcesTool",
    "ReportFindings",
    "Skill",
    "TaskOutput",
    "TodoWrite",
    "ToolSearch",
})

NETWORK_TOOLS = frozenset({"WebFetch", "WebSearch"})

# Tools that can change repository, environment, or external state through a
# channel this adapter does not model, including delegation to sessions whose
# individual tool calls it cannot guarantee it observes. Denied outright with
# an RFI instruction rather than passed through.
UNSUPPORTED_MUTATION_TOOLS = frozenset({
    "Agent",
    "Artifact",
    "CronCreate",
    "CronDelete",
    "DesignSync",
    "EnterWorktree",
    "ExitWorktree",
    "PushNotification",
    "RemoteTrigger",
    "ScheduleWakeup",
    "SendMessage",
    "SendUserFile",
    "TaskStop",
    "Workflow",
})

MCP_TOOL_PREFIX = "mcp__"

SHELL_MODES = ("denied", "restricted", "allowed")
NETWORK_MODES = ("denied", "allowed")
CAPABILITY_MODES = {
    "shell.execute": SHELL_MODES,
    "network.egress": NETWORK_MODES,
    "package.install": ("denied", "allowed"),
    "secrets.read": ("denied", "allowed"),
    "git.commit": ("denied", "allowed"),
    "git.push": ("denied", "allowed"),
}
KNOWN_GRANT_KEYS = frozenset({
    "filesystem.write", "filesystem.read.deny", *CAPABILITY_MODES,
})
SUPPORTED_PYTHON_MIN = (3, 10)
SUPPORTED_PYTHON_MAX = (3, 14)

RFI = ("File an RFI; the Owner amends the work order. You do not.")

POINTER_RELPATH = (".claude", "active-wo.txt")
WO_DIR_RELPATH = ("governance", "work-orders")
DENIAL_LOG_RELPATH = ("governance", "LOG-denials.jsonl")
CONTROL_PLANE_STATIC_RELPATHS = (
    POINTER_RELPATH,
    (".claude", "hooks", "wo_capability_wall.py"),
    (".claude", "settings.json"),
    (".claude", "settings.local.json"),
    DENIAL_LOG_RELPATH,
)
CONTROL_PLANE_STATIC_SCOPES = (
    (".claude", "hooks"),
)

# Bump only when the record shape changes in a way a reader must notice.
SCHEMA_VERSION = 1

# Classification results.
NONMUTATING = "nonmutating"
FILE_EDIT = "file_edit"
FILE_READ = "file_read"
SHELL = "shell"
NETWORK = "network"
UNSUPPORTED = "unsupported"

# Surface names written to the denial log.
SURFACE_BY_KIND = {
    FILE_EDIT: "filesystem.write",
    FILE_READ: "filesystem.read",
    SHELL: "shell.execute",
    NETWORK: "network.egress",
    UNSUPPORTED: "unmodeled",
}
SURFACE_UNKNOWN = "unknown"

# --------------------------------------------------------------------------
# Stable reason codes. These are an interface: a reader or downstream check may
# match on them, so a code is never renamed or reused for a different meaning.
# The mapped sentence is what reaches the log, and it must never carry a tool
# argument, a path taken from tool input, or any machine-specific value.
# --------------------------------------------------------------------------

SAFE_REASONS = {
    "hook_event_malformed": "Hook event was not a JSON object.",
    "tool_not_modeled": "Tool is not modeled by this capability wall.",
    "no_active_work_order": "No active work order; the pointer file is absent.",
    "pointer_unreadable": "Active work-order pointer could not be read.",
    "pointer_not_regular": "Active work-order pointer is not a regular file.",
    "pointer_empty": "Active work-order pointer is empty.",
    "pointer_backslash": "Active work-order pointer contains a backslash.",
    "pointer_names_no_file": "Active work-order pointer names no file.",
    "pointer_not_relative": "Active work-order pointer is not repository-relative.",
    "pointer_escapes_repository": "Active work-order pointer escapes the repository.",
    "pointer_not_markdown": "Active work-order pointer does not name a Markdown file.",
    "pointer_outside_work_orders": "Active work-order pointer resolves outside governance/work-orders/.",
    "pointer_is_directory": "Active work-order pointer names a directory.",
    "pointer_missing_file": "Active work-order pointer names a file that does not exist.",
    "work_order_unreadable": "Active work order could not be read.",
    "frontmatter_missing_open_fence": "Active work order has no opening frontmatter fence.",
    "frontmatter_missing_close_fence": "Active work order has no closing frontmatter fence.",
    "work_order_status_invalid": (
        "Active work order must declare exactly one ACTIVE status and no retirement metadata."
    ),
    "grant_missing": "Active work order declares no grant mapping.",
    "grant_structure_invalid": "Active work-order grant structure is invalid.",
    "shell_execute_denied": "grant.shell.execute is denied.",
    "shell_execute_invalid": "grant.shell.execute has an invalid value.",
    "control_plane_channel_uninspectable": (
        "Mutation-capable channel cannot prove protected control-plane targets remain unchanged."
    ),
    "network_egress_denied": "grant.network.egress is denied.",
    "network_egress_invalid": "grant.network.egress is absent or invalid.",
    "filesystem_write_missing": "Grant declares no filesystem.write.",
    "filesystem_write_empty": "grant.filesystem.write is empty.",
    "grant_path_invalid": "A grant.filesystem.write entry uses unsupported path syntax.",
    "write_target_undeterminable": "File-edit call has no determinable write target.",
    "write_target_path_invalid": "File-edit target uses unsupported path syntax.",
    "write_target_out_of_grant": "Write target is outside grant.filesystem.write.",
    "control_plane_protected": "Mutation of a protected control-plane artifact is denied.",
    "read_deny_path_invalid": "A grant.filesystem.read.deny entry uses unsupported path syntax.",
    "read_target_undeterminable": "Filesystem-read call has no determinable read target.",
    "read_target_outside_repository": "Read target could not be resolved inside the repository.",
    "read_target_denied": "Read target is inside a grant.filesystem.read.deny subtree.",
    "read_traversal_denied": "Read traversal could reach a grant.filesystem.read.deny subtree.",
    "read_pattern_invalid": "Read traversal pattern cannot be proven confined to its declared root.",
}


class Denied(Exception):
    """Raised internally to unwind to a deny decision with a reason and code."""

    def __init__(self, reason: str, code: str):
        super().__init__(reason)
        self.code = code


class Denial(str):
    """The provider-facing reason, carrying the structured evidence fields.

    Subclasses str so every caller can keep treating a denial as its reason
    text, while log_denial() reads the structured fields off it.
    """

    __slots__ = ("code", "surface", "work_order")

    def __new__(cls, reason: str, code: str, surface: str, work_order=None):
        obj = super().__new__(cls, " ".join(str(reason).split()))
        obj.code = code
        obj.surface = surface
        obj.work_order = work_order
        return obj

    @property
    def safe_reason(self) -> str:
        """The evidence-safe sentence written to the denial log."""
        return SAFE_REASONS.get(self.code, "Denied.")


def classify_tool(tool_name: object) -> str:
    """Classify a tool name. Anything unrecognized is UNSUPPORTED (fail closed)."""
    if not isinstance(tool_name, str) or not tool_name:
        return UNSUPPORTED
    if tool_name.startswith(MCP_TOOL_PREFIX):
        return UNSUPPORTED
    if tool_name in FILE_EDIT_TOOLS:
        return FILE_EDIT
    if tool_name in READ_TOOLS:
        return FILE_READ
    if tool_name in SHELL_TOOLS:
        return SHELL
    if tool_name in NETWORK_TOOLS:
        return NETWORK
    if tool_name in NONMUTATING_TOOLS:
        return NONMUTATING
    return UNSUPPORTED


# --------------------------------------------------------------------------
# Work-order pointer
# --------------------------------------------------------------------------

def resolve_pointer(repo_root: Path) -> Path:
    """Return the active work-order file, or raise Denied with the reason.

    The pointer must be UTF-8 readable, nonempty, repository-relative, free of
    '..' escapes, resolve inside governance/work-orders/, name a Markdown
    file, and be readable.
    """
    pointer_file = repo_root.joinpath(*POINTER_RELPATH)
    try:
        pointer_stat = pointer_file.lstat()
    except FileNotFoundError:
        raise Denied(
            "No active work order (.claude/active-wo.txt is missing). "
            "With no work order, no mutating action is permitted (Doctrine 7.3.2). "
            "Ask the Owner to activate a work order.",
            "no_active_work_order",
        )
    except OSError as exc:
        raise Denied(
            f"Active work-order pointer cannot be inspected ({type(exc).__name__}). {RFI}",
            "pointer_unreadable",
        ) from exc
    if not stat.S_ISREG(pointer_stat.st_mode):
        raise Denied(
            f"Active work-order pointer is not a regular file. {RFI}",
            "pointer_not_regular",
        )
    try:
        raw = pointer_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise Denied(
            f"Active work-order pointer is unreadable ({type(exc).__name__}). {RFI}",
            "pointer_unreadable",
        ) from exc

    pointer = raw.strip()
    if not pointer:
        raise Denied(f"Active work-order pointer is empty. {RFI}", "pointer_empty")
    if "\\" in pointer:
        raise Denied(
            f"Active work-order pointer {pointer!r} contains a backslash. "
            f"Use a forward-slash repository-relative path. {RFI}",
            "pointer_backslash",
        )

    parts = [p for p in pointer.split("/") if p not in ("", ".")]
    if not parts:
        raise Denied(
            f"Active work-order pointer {pointer!r} names no file. {RFI}",
            "pointer_names_no_file",
        )
    if pointer.startswith("/") or ":" in parts[0]:
        raise Denied(
            f"Active work-order pointer {pointer!r} is not repository-relative. {RFI}",
            "pointer_not_relative",
        )
    if ".." in parts:
        raise Denied(
            f"Active work-order pointer {pointer!r} escapes the repository with '..'. {RFI}",
            "pointer_escapes_repository",
        )
    if not parts[-1].lower().endswith(".md"):
        raise Denied(
            f"Active work-order pointer {pointer!r} does not name a Markdown file. {RFI}",
            "pointer_not_markdown",
        )

    wo_dir = repo_root.joinpath(*WO_DIR_RELPATH).resolve()
    wo_file = repo_root.joinpath(*parts).resolve()
    if wo_dir not in wo_file.parents:
        raise Denied(
            f"Active work-order pointer {pointer!r} resolves outside "
            f"{'/'.join(WO_DIR_RELPATH)}/. {RFI}",
            "pointer_outside_work_orders",
        )
    if wo_file.is_dir():
        raise Denied(
            f"Active work-order pointer {pointer!r} names a directory, not a file. {RFI}",
            "pointer_is_directory",
        )
    if not wo_file.is_file():
        raise Denied(
            f"Active work-order pointer names a missing file ({pointer}). {RFI}",
            "pointer_missing_file",
        )
    return wo_file


def work_order_relpath(repo_root: Path, wo_file: Path):
    """Repository-relative POSIX path of the work order, or None.

    Used only for the denial log, which must never carry an absolute path.
    """
    try:
        return wo_file.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def active_work_order_relpath(repo_root: Path):
    """Best-effort repository-relative active-WO path, or None if unresolvable."""
    try:
        return work_order_relpath(repo_root, resolve_pointer(repo_root))
    except Denied:
        return None
    except OSError:
        return None


# --------------------------------------------------------------------------
# Frontmatter and grant
# --------------------------------------------------------------------------

def extract_frontmatter(text: str) -> list[str]:
    """Return the frontmatter lines between the opening and closing '---'.

    Raises Denied when the opening fence is not the first line or the closing
    fence is absent.
    """
    lines = text.splitlines()
    if lines and lines[0].startswith("﻿"):
        lines[0] = lines[0][1:]
    if not lines or lines[0].strip() != "---":
        raise Denied(
            "Active work order does not begin with a '---' frontmatter fence. "
            f"A work order without a readable capability grant grants nothing. {RFI}",
            "frontmatter_missing_open_fence",
        )
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]
    raise Denied(
        f"Active work-order frontmatter has no closing '---' fence. {RFI}",
        "frontmatter_missing_close_fence",
    )


def _split_inline_list(raw: str) -> list[str]:
    inner = raw.strip()[1:-1]
    return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]


def _scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _strip_unquoted_comment(raw: str) -> str:
    quote = None
    for index, char in enumerate(raw):
        if quote:
            if char == quote:
                quote = None
            continue
        if char in ("'", '"'):
            quote = char
            continue
        if char == "#" and index > 0 and raw[index - 1] in (" ", "\t"):
            return raw[:index].rstrip()
    return raw


def parse_grant(frontmatter_lines: list[str]) -> dict:
    """Parse the Appendix B grant block.

    Returns {"filesystem.write": [...], "shell.execute": str | None,
    "filesystem.read.deny": [...] | None}. Absence of filesystem.read.deny
    (None) and an explicit empty list both mean "denies nothing" (B.3.3.7).
    Raises Denied when no 'grant:' mapping is present.
    """
    status_values = []
    retirement_fields = []
    for raw_line in frontmatter_lines:
        stripped = raw_line.strip()
        indent = len(raw_line) - len(raw_line.lstrip())
        if not stripped or stripped.startswith("#") or indent != 0 or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        if key == "status":
            status_values.append(_scalar(value.split(" #", 1)[0]))
        elif key in {"void", "superseded_by"}:
            retirement_fields.append(key)
    if (len(status_values) != 1 or status_values[0] != "ACTIVE"
            or retirement_fields):
        raise Denied(
            "Active work order must declare exactly one top-level status with "
            "value ACTIVE and no retirement metadata before any mutation is "
            f"permitted. {RFI}",
            "work_order_status_invalid",
        )

    grant: dict = {
        "status": "ACTIVE",
        "filesystem.write": None,
        "shell.execute": None,
        "network.egress": None,
        "filesystem.read.deny": None,
    }
    seen_grant = False
    in_grant = False
    list_key = None
    grant_indent = 0
    seen_child_keys: set[str] = set()

    for raw_line in frontmatter_lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip())

        if not in_grant:
            if indent == 0 and ":" in stripped:
                key, _, value = stripped.partition(":")
                if key.strip() != "grant":
                    continue
                if seen_grant or value.split(" #", 1)[0].strip():
                    raise Denied(
                        "Active work order must declare exactly one top-level "
                        "grant mapping with no scalar value. " + RFI,
                        "grant_structure_invalid",
                    )
                seen_grant = True
                in_grant = True
                grant_indent = indent
                list_key = None
            continue

        if indent <= grant_indent:
            # Left the grant mapping.
            in_grant = False
            list_key = None
            if indent == 0 and ":" in stripped:
                key, _, value = stripped.partition(":")
                if key.strip() == "grant":
                    raise Denied(
                        "Active work order declares more than one top-level "
                        "grant mapping. " + RFI,
                        "grant_structure_invalid",
                    )
            continue

        child_indent = grant_indent + 2
        if (list_key is not None and indent == child_indent + 2
                and stripped.startswith("- ")):
            grant[list_key].append(_scalar(_strip_unquoted_comment(stripped[2:])))
            continue
        if indent != child_indent:
            raise Denied(
                "Active work-order grant has unsupported indentation or a nested "
                f"mapping at {stripped!r}. {RFI}",
                "grant_structure_invalid",
            )
        list_key = None

        if ":" not in stripped:
            raise Denied(
                "Active work-order grant contains a malformed child entry. " + RFI,
                "grant_structure_invalid",
            )
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.split(" #", 1)[0].strip()
        if key not in KNOWN_GRANT_KEYS:
            raise Denied(
                f"Active work-order grant contains unsupported key {key!r}. {RFI}",
                "grant_structure_invalid",
            )
        if key in seen_child_keys:
            raise Denied(
                f"Active work-order grant repeats key {key!r}. {RFI}",
                "grant_structure_invalid",
            )
        seen_child_keys.add(key)

        if key in ("filesystem.write", "filesystem.read.deny"):
            if value.startswith("[") and value.endswith("]"):
                grant[key] = _split_inline_list(value)
            elif value:
                raise Denied(
                    f"grant.{key} must be a list, not a scalar. {RFI}",
                    "grant_structure_invalid",
                )
            else:
                grant[key] = []
                list_key = key
        else:
            grant[key] = _scalar(value)

    if not seen_grant:
        raise Denied(
            "Active work order declares no 'grant:' mapping. A work order "
            f"without a capability grant authorizes nothing (Doctrine 2.12). {RFI}",
            "grant_missing",
        )
    for key, modes in CAPABILITY_MODES.items():
        value = grant.get(key)
        if value is None:
            continue
        if value not in modes:
            code = ("shell_execute_invalid" if key == "shell.execute" else
                    "network_egress_invalid" if key == "network.egress" else
                    "grant_structure_invalid")
            raise Denied(f"grant.{key} has an invalid value. {RFI}", code)
    for key in ("filesystem.write", "filesystem.read.deny"):
        values = grant.get(key)
        if values is not None and len(values) != len(set(values)):
            raise Denied(f"grant.{key} contains a duplicate entry. {RFI}",
                         "grant_structure_invalid")
    return grant


def shell_mode(grant: dict) -> str:
    """Return the declared shell mode. Absent means denied (fail closed)."""
    mode = grant.get("shell.execute")
    if mode is None:
        return "denied"
    return mode


# --------------------------------------------------------------------------
# Grant path syntax
# --------------------------------------------------------------------------

def _is_linklike(path: Path) -> bool:
    """True for a symlink or a Windows junction/reparse directory."""
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

def _parse_scoped_path(entry: object, repo_root: Path, grant_key: str,
                       invalid_code: str) -> tuple[Path, bool]:
    """Validate one repository-relative grant-path entry for `grant_key`.

    Supported syntax is deliberately narrow: an exact repository-relative
    file or directory path, or that path followed by '/**' for the recursive
    subtree. Returns (resolved_base, recursive). Raises Denied otherwise.
    Shared by grant.filesystem.write and grant.filesystem.read.deny, which
    use identical path grammar (B.3.3.7).
    """
    if not isinstance(entry, str) or not entry.strip():
        raise Denied(
            f"{grant_key} contains an empty or non-string entry ({entry!r}). {RFI}",
            invalid_code,
        )
    text = entry.strip()

    if any(ord(character) < 32 for character in text):
        raise Denied(
            f"{grant_key} entry contains a control character. {RFI}",
            invalid_code,
        )
    if "\\" in text:
        raise Denied(
            f"{grant_key} entry {entry!r} contains a backslash. "
            f"Use forward-slash repository-relative paths. {RFI}",
            invalid_code,
        )
    if text.startswith("~"):
        raise Denied(
            f"{grant_key} entry {entry!r} uses home-directory expansion. {RFI}",
            invalid_code,
        )

    recursive = False
    if text.endswith("/**"):
        recursive = True
        text = text[: -len("/**")]
    if "*" in text:
        raise Denied(
            f"{grant_key} entry {entry!r} uses unsupported wildcard syntax. "
            "Only an exact path, or a path with a trailing '/**' recursive subtree, "
            f"is supported. '/*' is not recursive and is not accepted. {RFI}",
            invalid_code,
        )

    if text.startswith("/"):
        raise Denied(
            f"{grant_key} entry {entry!r} is not repository-relative. {RFI}",
            invalid_code,
        )
    if not text or text.endswith("/") or "//" in text:
        raise Denied(
            f"{grant_key} entry {entry!r} contains an empty path component or "
            f"names the repository root. {RFI}",
            invalid_code,
        )
    parts = text.split("/")
    if ":" in parts[0]:
        raise Denied(
            f"{grant_key} entry {entry!r} is not repository-relative. {RFI}",
            invalid_code,
        )
    if ".." in parts:
        raise Denied(
            f"{grant_key} entry {entry!r} escapes the repository with '..'. {RFI}",
            invalid_code,
        )
    if "." in parts:
        raise Denied(
            f"{grant_key} entry {entry!r} contains '.'. {RFI}",
            invalid_code,
        )

    lexical = repo_root
    for part in parts:
        lexical = lexical / part
        if _is_linklike(lexical):
            raise Denied(
                f"{grant_key} entry {entry!r} traverses a symlink or junction. {RFI}",
                invalid_code,
            )

    base = lexical.resolve()
    root = repo_root.resolve()
    if base == root or root not in base.parents:
        raise Denied(
            f"{grant_key} entry {entry!r} resolves to the repository root or "
            f"outside the repository. {RFI}",
            invalid_code,
        )
    return base, recursive


def parse_grant_path(entry: object, repo_root: Path) -> tuple[Path, bool]:
    """Validate one grant.filesystem.write entry. See _parse_scoped_path."""
    return _parse_scoped_path(entry, repo_root, "grant.filesystem.write", "grant_path_invalid")


def parse_read_deny_path(entry: object, repo_root: Path) -> tuple[Path, bool]:
    """Validate one grant.filesystem.read.deny entry. See _parse_scoped_path."""
    return _parse_scoped_path(entry, repo_root, "grant.filesystem.read.deny",
                              "read_deny_path_invalid")


def runtime_contract(frontmatter_lines: list[str], repo_root: Path,
                     work_order_relpath: str | None = None) -> dict:
    """Normalize the frontmatter subset consumed by the standalone wall.

    This small public contract is exercised against the dispatch parser's
    independent implementation so parser drift is deterministic and visible.
    """
    grant = parse_grant(frontmatter_lines)
    write_entries = grant.get("filesystem.write")
    if write_entries is not None:
        for entry in write_entries:
            parse_grant_path(entry, repo_root)
    deny_entries = grant.get("filesystem.read.deny") or []
    for entry in deny_entries:
        parse_read_deny_path(entry, repo_root)
    shell = shell_mode(grant)
    if shell not in SHELL_MODES:
        raise Denied("grant.shell.execute has an invalid value.", "shell_execute_invalid")
    network = grant.get("network.egress")
    if network not in NETWORK_MODES:
        raise Denied("grant.network.egress is absent or invalid.", "network_egress_invalid")
    protected = {"/".join(parts) for parts in CONTROL_PLANE_STATIC_RELPATHS}
    protected.update("/".join(parts) + "/**" for parts in CONTROL_PLANE_STATIC_SCOPES)
    if work_order_relpath is not None:
        protected.add(work_order_relpath)
    return {
        "status": grant["status"],
        "filesystem.write": list(write_entries or []),
        "filesystem.read.deny": list(deny_entries),
        "shell.execute": shell,
        "network.egress": network,
        "protected_control_plane": sorted(protected),
    }


def target_permitted(target: Path, entries: list, repo_root: Path) -> bool:
    """True when the resolved target is covered by any grant entry.

    Comparison is on resolved path components, never on string prefixes, so
    that 'governance/scratch2' is not covered by 'governance/scratch'.
    """
    for entry in entries:
        base, recursive = parse_grant_path(entry, repo_root)
        if target == base:
            return True
        if recursive and base in target.parents:
            return True
    return False


def protected_control_plane_paths(repo_root: Path, wo_file: Path) -> frozenset[Path]:
    """Resolved 8.7.1 paths protected independently of grant authorship."""
    protected = {
        repo_root.joinpath(*parts).resolve()
        for parts in CONTROL_PLANE_STATIC_RELPATHS
    }
    protected.add(wo_file.resolve())
    return frozenset(protected)


def _portable_alias_parts(path: Path, repo_root: Path):
    """Host-independent case/trailing-space-dot spelling under the root."""
    try:
        relative = Path(os.path.abspath(path)).relative_to(
            Path(os.path.abspath(repo_root)))
    except ValueError:
        return None
    return tuple(part.rstrip(" .").casefold() for part in relative.parts)


def is_protected_control_plane_target(target: Path, repo_root: Path,
                                      wo_file: Path, lexical_target=None) -> bool:
    """True for exact protected files or anything in a protected subtree."""
    root = repo_root.resolve()
    exact = protected_control_plane_paths(root, wo_file)
    if target in exact:
        return True
    scope_bases = [root.joinpath(*parts).resolve()
                   for parts in CONTROL_PLANE_STATIC_SCOPES]
    if any(target == base or base in target.parents for base in scope_bases):
        return True

    # Windows and commonly configured macOS filesystems treat case and
    # trailing-space/dot spellings as aliases, sometimes before a target exists.
    # Compare the lexical spelling as well as the resolved path, and do it on
    # every host so a grant never changes meaning across machines.
    candidate = target if lexical_target is None else Path(lexical_target)
    parts = _portable_alias_parts(candidate, root)
    if parts is None:
        return False
    protected_aliases = {
        tuple(part.rstrip(" .").casefold() for part in relative)
        for relative in CONTROL_PLANE_STATIC_RELPATHS
    }
    wo_alias = _portable_alias_parts(wo_file, root)
    if wo_alias is not None:
        protected_aliases.add(wo_alias)
    if parts in protected_aliases:
        return True
    hook_scope = tuple(part.casefold() for part in CONTROL_PLANE_STATIC_SCOPES[0])
    if len(parts) >= len(hook_scope) and parts[:len(hook_scope)] == hook_scope:
        return True
    return False


def edit_target(tool_input: object) -> str:
    """Return the write target of a file-edit call, or raise Denied."""
    if isinstance(tool_input, dict):
        for key in ("file_path", "notebook_path", "path"):
            value = tool_input.get(key)
            if isinstance(value, str) and value.strip():
                return value
    raise Denied(
        "File-edit call has no determinable write target. A wall that cannot "
        f"see the target cannot permit it. {RFI}",
        "write_target_undeterminable",
    )


# --------------------------------------------------------------------------
# grant.filesystem.read.deny (B.3.3)
# --------------------------------------------------------------------------

def resolve_repo_path(target_text: str, repo_root: Path) -> Path:
    """Resolve a tool-supplied path against repo_root.

    Raises Denied('read_target_outside_repository') when the resolved path
    cannot be proven to lie inside the repository: an absolute path outside
    it, or a relative path that escapes it with '..'. Conservative by design
    (B.3.3.8): an undeterminable or escaping read target fails closed rather
    than defaulting to allowed.
    """
    candidate = Path(target_text)
    target = (candidate if candidate.is_absolute() else repo_root / candidate).resolve()
    root = repo_root.resolve()
    if target != root and root not in target.parents:
        raise Denied(
            f"Read target could not be resolved inside the repository. {RFI}",
            "read_target_outside_repository",
        )
    return target


def exact_read_target(tool: str, tool_input: object) -> str:
    """Return the exact read target for Read/NotebookRead, or raise Denied."""
    key = EXACT_READ_TOOL_KEYS[tool]
    if isinstance(tool_input, dict):
        value = tool_input.get(key)
        if isinstance(value, str) and value.strip():
            return value
    raise Denied(
        f"{tool} call has no determinable read target. A wall that cannot "
        f"see the target cannot permit it. {RFI}",
        "read_target_undeterminable",
    )


def traversal_read_root(tool_input: object, repo_root: Path) -> str:
    """Return the traversal root text for Glob/Grep/LS.

    An absent or blank 'path' means the repository root (B.3.3.8).
    """
    if isinstance(tool_input, dict):
        value = tool_input.get("path")
        if isinstance(value, str) and value.strip():
            return value
    return str(repo_root)


def validate_traversal_pattern(tool: str, tool_input: object) -> None:
    """Accept only a small pattern grammar provably confined to its root.

    Literal path components plus ``*``, ``**`` and ``?`` wildcards are modeled.
    Provider-dependent expansion forms (braces, character classes, home
    expansion, backslashes and drive/absolute forms) fail closed.
    """
    if not isinstance(tool_input, dict):
        return
    key = "pattern" if tool == "Glob" else "glob" if tool == "Grep" else None
    if key is None:
        return
    value = tool_input.get(key)
    if value is None and tool == "Grep":
        return
    if not isinstance(value, str):
        raise Denied(
            f"{tool} has a malformed path-bearing pattern. {RFI}",
            "read_pattern_invalid",
        )
    normalized = value.replace("\\", "/")
    parts = normalized.split("/")
    allowed = frozenset(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.*?/"
    )
    unsafe_dot_wildcard = any(
        part not in {"*", "**"}
        and not part.replace("*", "").replace("?", "").strip(".")
        and any(char in part for char in "*?")
        for part in parts
    )
    if (not value or normalized.startswith("/") or (parts and ":" in parts[0])
            or any(part in ("", ".", "..") for part in parts)
            or any(char not in allowed for char in value)
            or "\\" in value or unsafe_dot_wildcard):
        raise Denied(
            f"{tool} pattern cannot be proven to stay inside its declared root. {RFI}",
            "read_pattern_invalid",
        )


def read_deny_entries_denied_for_exact_target(target: Path, deny_entries: list,
                                              repo_root: Path) -> bool:
    """True when `target` is the denied path or lies below a recursive one."""
    for entry in deny_entries:
        base, recursive = parse_read_deny_path(entry, repo_root)
        if target == base:
            return True
        if recursive and base in target.parents:
            return True
    return False


def read_deny_entries_denied_for_traversal_root(root: Path, deny_entries: list,
                                                repo_root: Path) -> bool:
    """True when traversal rooted at `root` overlaps a denied subtree.

    Conservative overlap (B.3.3.8): denied when the root lies inside a denied
    base (root == base or root is a descendant), or when the root is an
    ancestor of a denied base, since a recursive traversal from an ancestor
    can reach a descendant denied subtree regardless of that entry's own
    recursive flag.
    """
    for entry in deny_entries:
        base, _recursive = parse_read_deny_path(entry, repo_root)
        if root == base or base in root.parents or root in base.parents:
            return True
    return False


def decide_file_read(event: dict, repo_root: Path, tool: str, shown: str):
    """Decide a FILE_READ call.

    No-work-order lockout (8.3.5.1) binds mutation tools, not ordinary
    read-only review sessions (B.3.3.10): an absent pointer leaves ordinary
    review available. Once a pointer exists, unreadable or malformed
    pointer/work-order/grant state fails closed for modeled reads with the same
    diagnostic stage used for mutation tools.
    """
    try:
        wo_file = resolve_pointer(repo_root)
    except Denied as exc:
        if exc.code == "no_active_work_order":
            return None
        return Denial(str(exc), exc.code, SURFACE_BY_KIND[FILE_READ])
    wo_rel = work_order_relpath(repo_root, wo_file)
    try:
        text = wo_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        denied = Denied(
            f"Active work order is unreadable ({type(exc).__name__}). {RFI}",
            "work_order_unreadable",
        )
        return Denial(str(denied), denied.code, SURFACE_BY_KIND[FILE_READ], wo_rel)
    try:
        grant = runtime_contract(extract_frontmatter(text), repo_root, wo_rel)
    except Denied as exc:
        return Denial(str(exc), exc.code, SURFACE_BY_KIND[FILE_READ], wo_rel)

    deny_entries = grant.get("filesystem.read.deny") or []
    if not deny_entries:
        return None

    try:
        if tool in EXACT_READ_TOOL_KEYS:
            target_text = exact_read_target(tool, event.get("tool_input"))
            target = resolve_repo_path(target_text, repo_root)
            if read_deny_entries_denied_for_exact_target(target, deny_entries, repo_root):
                raise Denied(
                    f"BLOCKED by {wo_file.name}: {target_text} is inside a "
                    f"grant.filesystem.read.deny subtree. {RFI}",
                    "read_target_denied",
                )
            return None

        # traversal/search tool (Glob, Grep, LS)
        validate_traversal_pattern(tool, event.get("tool_input"))
        root_text = traversal_read_root(event.get("tool_input"), repo_root)
        root = resolve_repo_path(root_text, repo_root)
        if read_deny_entries_denied_for_traversal_root(root, deny_entries, repo_root):
            raise Denied(
                f"BLOCKED by {wo_file.name}: {shown} rooted at {root_text} could "
                f"traverse a grant.filesystem.read.deny subtree. {RFI}",
                "read_traversal_denied",
            )
        return None
    except Denied as exc:
        return Denial(str(exc), exc.code, SURFACE_BY_KIND[FILE_READ], wo_rel)


# --------------------------------------------------------------------------
# Decision
# --------------------------------------------------------------------------

def decide(event: object, repo_root: Path):
    """Return a Denial, or None to allow.

    Pure: performs no writes. main() handles logging and process exit. The
    returned Denial is a str carrying the provider-facing reason, plus the
    reason code, surface, and repository-relative work-order path used by the
    denial log.
    """
    if not isinstance(event, dict):
        return Denial(
            f"Hook event is not a JSON object. {RFI}",
            "hook_event_malformed",
            SURFACE_UNKNOWN,
        )

    tool = event.get("tool_name")
    kind = classify_tool(tool)
    shown = tool if isinstance(tool, str) and tool else "<unnamed tool>"
    surface = SURFACE_BY_KIND.get(kind, SURFACE_UNKNOWN)

    if kind == NONMUTATING:
        return None

    if kind == UNSUPPORTED:
        return Denial(
            f"BLOCKED: {shown} is not modeled by this capability wall, so its "
            "authority cannot be verified against the active work order's grant. "
            "Tools that write, schedule, publish, or delegate to another session "
            "are denied until classified in the adapter. Doctrine 8.3.3 requires a "
            f"wall to cover every mutation channel reaching a surface. {RFI}",
            "tool_not_modeled",
            surface,
            active_work_order_relpath(repo_root),
        )

    if kind == FILE_READ:
        return decide_file_read(event, repo_root, tool, shown)

    wo_rel = None
    try:
        wo_file = resolve_pointer(repo_root)
        wo_rel = work_order_relpath(repo_root, wo_file)
        try:
            text = wo_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise Denied(
                f"Active work order is unreadable ({type(exc).__name__}). {RFI}",
                "work_order_unreadable",
            ) from exc

        grant = parse_grant(extract_frontmatter(text))

        if kind == NETWORK:
            mode = grant.get("network.egress")
            if mode == "denied":
                raise Denied(
                    f"BLOCKED by {wo_file.name}: grant.network.egress is denied, "
                    f"so {shown} is denied. {RFI}",
                    "network_egress_denied",
                )
            if mode not in NETWORK_MODES:
                raise Denied(
                    f"BLOCKED by {wo_file.name}: grant.network.egress is absent or "
                    f"invalid; {shown} is denied. {RFI}",
                    "network_egress_invalid",
                )
            return None

        if kind == SHELL:
            mode = shell_mode(grant)
            if mode == "denied":
                raise Denied(
                    f"BLOCKED by {wo_file.name}: grant.shell.execute is denied, "
                    f"so {shown} is denied. {RFI}",
                    "shell_execute_denied",
                )
            if mode not in SHELL_MODES:
                raise Denied(
                    f"BLOCKED by {wo_file.name}: grant.shell.execute has invalid "
                    f"value {mode!r} (expected one of {', '.join(SHELL_MODES)}). "
                    f"{shown} denied. {RFI}",
                    "shell_execute_invalid",
                )
            raise Denied(
                f"BLOCKED by {wo_file.name}: {shown} can mutate protected "
                "control-plane artifacts without exposing an exact target to "
                f"this wall. Doctrine 8.7 requires categorical denial. {RFI}",
                "control_plane_channel_uninspectable",
            )

        # kind == FILE_EDIT
        entries = grant.get("filesystem.write")
        if entries is None:
            raise Denied(
                f"BLOCKED by {wo_file.name}: the grant declares no "
                f"filesystem.write, so it carries no file-edit authority. {RFI}",
                "filesystem_write_missing",
            )
        for entry in entries:
            parse_grant_path(entry, repo_root)
        target_text = edit_target(event.get("tool_input"))
        candidate = Path(target_text)
        if ".." in candidate.parts:
            raise Denied(
                f"BLOCKED by {wo_file.name}: {target_text} contains a parent "
                f"traversal segment; textual aliases cannot carry authority. {RFI}",
                "write_target_path_invalid",
            )
        lexical_target = candidate if candidate.is_absolute() else repo_root / candidate
        try:
            relative_lexical = Path(os.path.abspath(lexical_target)).relative_to(
                Path(os.path.abspath(repo_root))
            )
        except ValueError:
            relative_lexical = None
        if relative_lexical is not None:
            current = repo_root
            for part in relative_lexical.parts:
                current = current / part
                if _is_linklike(current):
                    raise Denied(
                        f"BLOCKED by {wo_file.name}: {target_text} traverses a "
                        f"symlink or junction target alias. {RFI}",
                        "write_target_path_invalid",
                    )
        target = lexical_target.resolve()
        root = repo_root.resolve()
        if target == root or root not in target.parents:
            raise Denied(
                f"BLOCKED by {wo_file.name}: {target_text} resolves to the "
                f"repository root or outside the repository. {RFI}",
                "write_target_path_invalid",
            )

        if is_protected_control_plane_target(
                target, repo_root, wo_file, lexical_target=lexical_target):
            raise Denied(
                f"BLOCKED by {wo_file.name}: {target_text} is a protected "
                f"control-plane artifact under Doctrine 8.7. {RFI}",
                "control_plane_protected",
            )

        if not entries:
            raise Denied(
                f"BLOCKED by {wo_file.name}: grant.filesystem.write is empty, "
                f"so no path is writable. {RFI}",
                "filesystem_write_empty",
            )
        if target_permitted(target, entries, repo_root):
            return None
        raise Denied(
            f"BLOCKED by {wo_file.name}: {target_text} is outside "
            f"grant.filesystem.write ({', '.join(str(e) for e in entries)}). {RFI}",
            "write_target_out_of_grant",
        )
    except Denied as exc:
        return Denial(str(exc), exc.code, surface, wo_rel)


# --------------------------------------------------------------------------
# Process entry point
# --------------------------------------------------------------------------

def repository_root() -> Path:
    """Return the validated project root for the one supported installation."""
    installed = Path(__file__).resolve()
    if (installed.name != "wo_capability_wall.py"
            or installed.parent.name != "hooks"
            or installed.parent.parent.name != ".claude"):
        raise RuntimeError(
            "adapter is not installed at <repo>/.claude/hooks/wo_capability_wall.py")
    root = installed.parents[2]
    declared = os.environ.get("CLAUDE_PROJECT_DIR")
    if not declared:
        raise RuntimeError(
            "CLAUDE_PROJECT_DIR is absent; repository identity cannot be verified")
    try:
        declared_root = Path(declared).resolve()
    except OSError as exc:
        raise RuntimeError("CLAUDE_PROJECT_DIR cannot be resolved") from exc
    if root != declared_root:
        raise RuntimeError(
            "installed adapter path does not belong to CLAUDE_PROJECT_DIR")
    return root


def hard_fail(message: str) -> None:
    """Blocking fallback: exit 2 is what PreToolUse honors as a hard block.

    An ordinary exit 1 traceback does not block the tool call.
    """
    sys.stderr.write(f"wo_capability_wall: {message}\n")
    sys.exit(2)


def utc_timestamp() -> str:
    """UTC RFC 3339, second precision. Injected in tests, never asserted live."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def session_identifier(event: object):
    """The provider session id when supplied as a string, otherwise None."""
    if isinstance(event, dict):
        value = event.get("session_id")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def denial_record(denial: Denial, tool, timestamp: str, session_id) -> dict:
    """Build the evidence-safe log record. Field order is stable."""
    return {
        "schema": SCHEMA_VERSION,
        "timestamp": timestamp,
        "session_id": session_id,
        "tool": tool if isinstance(tool, str) and tool else None,
        "surface": denial.surface,
        "work_order": denial.work_order,
        "decision": "deny",
        "reason_code": denial.code,
        "reason": denial.safe_reason,
    }


def log_denial(repo_root: Path, denial: Denial, tool=None,
               timestamp=None, session_id=None) -> None:
    """Append one JSON Lines record. Never raises; never opens the wall.

    newline="" suppresses platform translation: the birth certificate is an
    evidence artifact and must be byte-identical across platforms.
    """
    record = denial_record(
        denial,
        tool,
        timestamp if timestamp is not None else utc_timestamp(),
        session_id,
    )
    log = repo_root.joinpath(*DENIAL_LOG_RELPATH)
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        with log.open("a", encoding="utf-8", newline="") as handle:
            handle.write(line + "\n")
    except (OSError, TypeError, ValueError):
        # Fail closed: the denial still stands even if it could not be recorded.
        pass


def emit_deny(reason: str) -> None:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": str(reason),
    }}))


class PreflightError(Exception):
    """A read-only installation/startup preflight failed."""


def supported_python_version(version_info=None) -> bool:
    """True only for the explicitly tested CPython minor-version range."""
    version = sys.version_info if version_info is None else version_info
    current = (int(version[0]), int(version[1]))
    return SUPPORTED_PYTHON_MIN <= current <= SUPPORTED_PYTHON_MAX


def preflight_payload(project_root: Path, settings_path: Path,
                      expected_digest: str, platform_name: str) -> dict:
    """Read-only validation of installation, registration, and startup facts."""
    if not supported_python_version():
        raise PreflightError(
            f"unsupported Python {sys.version_info.major}.{sys.version_info.minor}; "
            f"supported range is {SUPPORTED_PYTHON_MIN[0]}.{SUPPORTED_PYTHON_MIN[1]} "
            f"through {SUPPORTED_PYTHON_MAX[0]}.{SUPPORTED_PYTHON_MAX[1]}"
        )
    host_platform = "windows" if os.name == "nt" else "posix"
    if platform_name != host_platform:
        raise PreflightError(
            f"requested {platform_name} preflight on native {host_platform} runtime"
        )
    root = project_root.resolve()
    installed = root.joinpath(*(".claude", "hooks", "wo_capability_wall.py")).resolve()
    if Path(__file__).resolve() != installed:
        raise PreflightError("adapter is not running from the project-root installed hook path")
    digest = hashlib.sha256(installed.read_bytes()).hexdigest()
    if digest.lower() != expected_digest.strip().lower():
        raise PreflightError("installed adapter digest does not match the expected digest")
    expected_settings = root.joinpath(".claude", "settings.json").resolve()
    if settings_path.resolve() != expected_settings:
        raise PreflightError("settings source is not the project registration file")
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError, TypeError) as exc:
        raise PreflightError(f"project settings are unreadable or invalid ({type(exc).__name__})")
    try:
        entries = settings["hooks"]["PreToolUse"]
        if not isinstance(entries, list) or len(entries) != 1:
            raise TypeError
        entry = entries[0]
        matcher = entry["matcher"]
        hooks = entry["hooks"]
        if matcher != "*" or not isinstance(hooks, list) or len(hooks) != 1:
            raise TypeError
        hook = hooks[0]
        command = hook["command"]
        timeout = hook["timeout"]
        if hook.get("type") != "command" or not isinstance(command, str):
            raise TypeError
        if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
            raise TypeError
    except (KeyError, TypeError):
        raise PreflightError(
            "settings must contain exactly one matcher '*' command hook with an explicit timeout"
        )
    portable_token = "${CLAUDE_PROJECT_DIR}/.claude/hooks/wo_capability_wall.py"
    interpreter = "py -3" if platform_name == "windows" else "python3"
    if portable_token not in command or not command.strip().startswith(interpreter + " "):
        raise PreflightError(
            f"registration is not portable or does not use the native {platform_name} command"
        )
    return {
        "ok": True,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "supported_python": (
            f"{SUPPORTED_PYTHON_MIN[0]}.{SUPPORTED_PYTHON_MIN[1]}-"
            f"{SUPPORTED_PYTHON_MAX[0]}.{SUPPORTED_PYTHON_MAX[1]}"
        ),
        "platform": platform_name,
        "installed_digest": digest,
        "matcher": matcher,
        "source": "project",
        "portable_registration": True,
        "timeout_seconds": timeout,
        "provider_limitation": (
            "If the provider does not invoke the hook because startup or timeout fails, "
            "this command hook cannot represent that absence as fail-closed."
        ),
    }


def run_preflight(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="wo_capability_wall.py --preflight")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--settings", required=True)
    parser.add_argument("--expected-digest", required=True)
    parser.add_argument("--platform", required=True, choices=("windows", "posix"))
    args = parser.parse_args(argv)
    try:
        payload = preflight_payload(
            Path(args.project_root), Path(args.settings),
            args.expected_digest, args.platform,
        )
    except (OSError, PreflightError) as exc:
        sys.stderr.write(f"wo_capability_wall preflight: {exc}\n")
        raise SystemExit(2)
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    raise SystemExit(0)


def main(argv: list[str] | None = None) -> None:
    args = list(() if argv is None else argv)
    if args[:1] == ["--preflight"]:
        run_preflight(args[1:])
    if args:
        hard_fail("unsupported command-line arguments")
    try:
        raw = sys.stdin.read()
    except Exception as exc:  # noqa: BLE001 - hard fallback must be total
        hard_fail(f"cannot read hook event from stdin ({type(exc).__name__})")
        return
    try:
        event = json.loads(raw)
    except (ValueError, TypeError):
        hard_fail("hook event is not valid JSON; blocking rather than passing through")
        return

    try:
        root = repository_root()
        denial = decide(event, root)
        if denial is None:
            sys.exit(0)
        tool = event.get("tool_name") if isinstance(event, dict) else None
        log_denial(root, denial, tool=tool, session_id=session_identifier(event))
        emit_deny(denial)
        sys.exit(0)
    except SystemExit:
        raise
    except RuntimeError as exc:
        hard_fail(str(exc))
    except Exception as exc:  # noqa: BLE001 - hard fallback must be total
        hard_fail(f"unexpected {type(exc).__name__} while evaluating the grant")


if __name__ == "__main__":
    main(sys.argv[1:])
