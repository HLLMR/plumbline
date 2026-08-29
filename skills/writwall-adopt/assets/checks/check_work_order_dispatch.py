#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Deterministic pre-dispatch validator for Writwall work-order state.

Standard library only. Read-only: this checker never repairs, creates, or
removes the activation pointer, never edits a work order, and never infers
Owner authority. It detects four observed defect classes before a mutating
Implementer session is launched:

  1. missing, misspelled, malformed, or wrongly targeted active pointer;
  2. CRLF or non-UTF-8 issued-work-order bytes;
  3. malformed or unsafe machine-readable grant/frontmatter, or a
     path-shaped B.3/B.4 token not resolved by the effective grant or an
     explicit typed exception;
  4. missing, malformed, overlapping, or incomplete Appendix B enforcement
     classification.

It also distinguishes legitimate lockout from defective activation and
detects issue-time cache/bytecode residue.

Usage:
    python checks/check_work_order_dispatch.py --lockout
    python checks/check_work_order_dispatch.py --active
    python checks/check_work_order_dispatch.py --work-order <repo-relative-path>
    python checks/check_work_order_dispatch.py --emit-boundaries --work-order <repo-relative-path>

Modes are mutually exclusive. There is no implicit mode: calling the tool
without one is a usage error, so a missing pointer can never be silently
read as either success or failure.

Design decision (RFI-28): `grant` in YAML frontmatter is the sole
machine-readable capability authority. Amendment prose may explain a change
but cannot independently extend it. This checker proves frontmatter
structure, path safety, supported values, and normalized effective-grant
output; it does not parse natural-language amendment prose. It additionally
scans path-shaped tokens (backtick-quoted, slash-containing, `..`-free) in
the B.3 and B.4 sections and requires each to resolve through
grant.filesystem.write, grant.filesystem.read.deny, or an explicit typed
dispatch_validation.prose_path_exceptions entry. An unmatched token is a
blocking warning (`prose_path_out_of_grant`) that fails the run. This is
pattern matching against known machine-readable sets, not prose
interpretation or inferred write authority.

This module deliberately does not import the capability-wall adapter
(adapters/claude-code/wo_capability_wall.py). Coupling validation to hook
startup or mutation behavior would coordinate module lifetimes for no
functional benefit; sharing parsing logic across the two would require
explicit shared design and tests of its own, not copy-paste drift between
two independently evolving files.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

POINTER_RELPATH = (".claude", "active-wo.txt")
WO_DIR_RELPATH = ("governance", "work-orders")

RESIDUE_DIR_NAMES = frozenset({
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
})
RESIDUE_FILE_SUFFIXES = (".pyc", ".pyo")

ID_RE = re.compile(r"^WO-(?:[A-Z][A-Z0-9]*-)?\d{3}$")

CAPABILITY_KEYS = (
    "shell.execute", "network.egress", "package.install",
    "secrets.read", "git.commit", "git.push",
)
CAPABILITY_VALUES = {
    "shell.execute": ("denied", "restricted", "allowed"),
    "network.egress": ("denied", "allowed"),
    "package.install": ("denied", "allowed"),
    "secrets.read": ("denied", "allowed"),
    "git.commit": ("denied", "allowed"),
    "git.push": ("denied", "allowed"),
}

REQUIRED_TOP_FIELDS = ("id", "status", "doctrine_rev", "grant")

LOCKOUT = "lockout"
CANDIDATE = "candidate"
ACTIVE = "active"
EMIT = "emit"


class DispatchError(Exception):
    """Raised internally to unwind to a stable (category, detail) failure."""

    def __init__(self, category: str, detail: str):
        super().__init__(detail)
        self.category = category
        self.detail = detail


class Failures:
    def __init__(self):
        self.items: list[str] = []

    def add(self, category: str, detail: str) -> None:
        self.items.append(f"[{category}] {detail}")

    def __bool__(self) -> bool:
        return bool(self.items)


# --------------------------------------------------------------------------
# Git baseline (read-only)
# --------------------------------------------------------------------------

def run_git(repo_root: Path, *args: str):
    try:
        return subprocess.run(
            ["git", *args], cwd=repo_root, capture_output=True,
            text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None


def check_git_baseline(repo_root: Path, failures: Failures) -> None:
    branch = run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")
    if branch is None or branch.returncode != 0 or not branch.stdout.strip():
        failures.add("git", "branch is not readable")
    head = run_git(repo_root, "rev-parse", "HEAD")
    if head is None or head.returncode != 0 or not head.stdout.strip():
        failures.add("git", "HEAD is not readable")
    staged = run_git(repo_root, "diff", "--cached", "--name-only")
    if staged is None:
        failures.add("git", "staged-change status is not readable")
    elif staged.stdout.strip():
        names = ", ".join(staged.stdout.split())
        failures.add("git", f"staged changes are present: {names}")


def repo_status_entries(repo_root: Path):
    # List individual untracked files. Git's default porcelain output folds a
    # wholly untracked directory to `dir/`, which would force an Owner to
    # allowlist the entire directory merely to authorize one exact new file.
    # That broader allowance could conceal an unrelated sibling.
    result = run_git(repo_root, "status", "--porcelain", "--untracked-files=all")
    if result is None or result.returncode != 0:
        return None
    entries = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        entries.append(path.strip('"').replace("\\", "/"))
    return entries


def check_dirty_tree(repo_root: Path, mode: str, allow: list[str],
                     wo_relpath: str | None, failures: Failures) -> None:
    entries = repo_status_entries(repo_root)
    if entries is None:
        failures.add("dirty-tree", "git status is not readable")
        return
    allowed = set(allow)
    if mode == ACTIVE:
        allowed.add("/".join(POINTER_RELPATH))
    if wo_relpath is not None:
        allowed.add(wo_relpath)
    for entry in entries:
        if entry in allowed:
            continue
        failures.add("dirty-tree", f"unexpected change outside the allowlist: {entry}")


# --------------------------------------------------------------------------
# Residue scan
# --------------------------------------------------------------------------

def check_residue(repo_root: Path, failures: Failures) -> None:
    for path in sorted(repo_root.rglob("*")):
        try:
            relative = path.relative_to(repo_root)
        except ValueError:
            continue
        parts = relative.parts
        if not parts or parts[0] == ".git":
            continue
        if path.is_dir():
            if path.name in RESIDUE_DIR_NAMES:
                failures.add("residue",
                             f"{relative.as_posix()} is a cache/bytecode residue directory")
            continue
        if path.is_file() and path.suffix.lower() in RESIDUE_FILE_SUFFIXES:
            failures.add("residue", f"{relative.as_posix()} is bytecode residue")


# --------------------------------------------------------------------------
# Active pointer
# --------------------------------------------------------------------------

def pointer_extension_siblings(repo_root: Path) -> list[str]:
    """Files in .claude/ matching active-wo.* other than the exact target."""
    claude_dir = repo_root / ".claude"
    if not claude_dir.is_dir():
        return []
    siblings = []
    for entry in sorted(claude_dir.iterdir()):
        if entry.name == "active-wo.txt":
            continue
        if re.match(r"^active-wo\.[^.]+$", entry.name):
            siblings.append(entry.name)
    return siblings


def exact_case_path(repo_root: Path, parts: tuple[str, ...]) -> Path | None:
    """The resolved Path only if every component matches on-disk case exactly.

    Works even on a case-insensitive filesystem: iterdir() returns the
    stored names, and Python set membership is always case-sensitive.
    """
    current = repo_root
    for part in parts:
        if current.is_symlink():
            return None
        try:
            names = {p.name for p in current.iterdir()}
        except OSError:
            return None
        if part not in names:
            return None
        current = current / part
    return current


def load_pointer(repo_root: Path, failures: Failures) -> str | None:
    """Return the repo-relative target text from .claude/active-wo.txt.

    Returns None (with a recorded failure) on any malformed pointer.
    """
    pointer_file = repo_root.joinpath(*POINTER_RELPATH)
    if not pointer_file.is_file():
        failures.add("pointer", "active pointer .claude/active-wo.txt does not exist")
        return None
    raw = pointer_file.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        failures.add("pointer", "active pointer has a UTF-8 BOM")
    if b"\x00" in raw:
        failures.add("pointer", "active pointer contains a NUL byte")
    if b"\r" in raw:
        failures.add("pointer", "active pointer contains CR bytes")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        failures.add("pointer", f"active pointer is not valid UTF-8: {exc}")
        return None
    lines = text.split("\n")
    non_empty = [l for l in lines if l.strip()]
    if len(non_empty) != 1 or (len(lines) > 2) or (len(lines) == 2 and lines[1] != ""):
        failures.add("pointer",
                     "active pointer must be exactly one non-empty line, "
                     "LF-terminated or unterminated")
        return None
    raw_value = non_empty[0]
    if raw_value != raw_value.strip():
        failures.add("pointer",
                     f"active pointer {raw_value!r} has leading or trailing whitespace; "
                     "it is rejected, never trimmed")
        return None
    value = raw_value
    if not value:
        failures.add("pointer", "active pointer is empty")
        return None
    if value.startswith("/") or ":" in value.split("/", 1)[0]:
        failures.add("pointer", f"active pointer {value!r} is not repository-relative")
        return None
    parts = value.split("/")
    if any(p == "" for p in parts):
        failures.add("pointer",
                     f"active pointer {value!r} contains an empty path component (a doubled, "
                     "leading, or trailing '/'); it is rejected, never normalized")
        return None
    if any(p == ".." for p in parts):
        failures.add("pointer", f"active pointer {value!r} escapes the repository with '..'")
        return None
    if parts[: len(WO_DIR_RELPATH)] != list(WO_DIR_RELPATH):
        failures.add("pointer",
                     f"active pointer {value!r} does not resolve under "
                     f"{'/'.join(WO_DIR_RELPATH)}/")
        return None
    return "/".join(parts)


def resolve_active_target(repo_root: Path, relpath: str, failures: Failures) -> Path | None:
    parts = tuple(relpath.split("/"))
    exact = exact_case_path(repo_root, parts)
    if exact is None:
        failures.add("pointer",
                     f"active pointer target {relpath!r} does not exist, is reached "
                     "through a symlink, or its case does not exactly match the "
                     "name on disk")
        return None
    if exact.is_symlink():
        failures.add("pointer", f"active pointer target {relpath!r} is a symlink")
        return None
    if not exact.is_file():
        failures.add("pointer", f"active pointer target {relpath!r} is not a regular file")
        return None
    return exact


# --------------------------------------------------------------------------
# Work-order bytes
# --------------------------------------------------------------------------

def load_work_order_text(path: Path, failures: Failures) -> str | None:
    if not path.is_file():
        failures.add("bytes", f"{path.name} is not an existing regular file "
                              "under governance/work-orders/")
        return None
    raw = path.read_bytes()
    ok = True
    if raw.startswith(b"\xef\xbb\xbf"):
        failures.add("bytes", "work order has a UTF-8 BOM")
        ok = False
    if b"\x00" in raw:
        failures.add("bytes", "work order contains a NUL byte")
        ok = False
    if b"\r" in raw:
        failures.add("bytes", "work order contains CR bytes (not LF-only)")
        ok = False
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        failures.add("bytes", f"work order is not valid UTF-8: {exc}")
        return None
    return text if ok else text


# --------------------------------------------------------------------------
# Frontmatter: a narrow, hand-rolled block-structure parser.
#
# Supports exactly the grammar this repository's work orders use: top-level
# `key: scalar` fields; a `key:` mapping continued as an indented block
# (nested mapping, or a block list of scalars / two-field mappings). Two
# spaces per indentation level. Anything else is a deterministic parse
# failure, never a guess.
# --------------------------------------------------------------------------

def frontmatter_slice(text: str, failures: Failures) -> list[str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        failures.add("frontmatter", "missing opening '---' fence as the first line")
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]
    failures.add("frontmatter", "missing closing '---' fence")
    return None


def _tokenize(lines: list[str]) -> list[tuple[int, str]]:
    tokens = []
    for raw in lines:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        content = raw.lstrip()
        indent = len(raw) - len(content)
        leading = raw[:indent]
        if "\t" in leading:
            raise DispatchError("frontmatter", f"line uses tab indentation: {raw!r}")
        if indent % 2 != 0:
            raise DispatchError("frontmatter", f"line uses odd (non-2-space) indentation: {raw!r}")
        tokens.append((indent, content.strip()))
    return tokens


def _scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _strip_unquoted_comment(raw: str) -> str:
    """Truncate `raw` at a '#' that is outside quotes and whitespace-led.

    A '#' inside a single- or double-quoted run is never treated as a
    comment start, so a literal scalar like "'quoted # value'" keeps its
    hash. Quote state is tracked char-by-char rather than assumed from the
    first character, since these are plain (unquoted) list scalars whose
    text may still legitimately contain a quoted substring.
    """
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


def _split_inline_list(raw: str) -> list[str]:
    inner = raw.strip()[1:-1]
    return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]


def _parse_block(tokens: list[tuple[int, str]], pos: int, indent: int):
    """Parse a block at exactly `indent`. Returns (value, next_pos)."""
    if pos >= len(tokens) or tokens[pos][0] != indent:
        return None, pos

    if tokens[pos][1].startswith("- "):
        items = []
        while pos < len(tokens) and tokens[pos][0] == indent and tokens[pos][1].startswith("- "):
            rest = tokens[pos][1][2:]
            pos += 1
            if ":" in rest:
                key, _, val = rest.partition(":")
                mapping = {key.strip(): _scalar(val)}
                field_indent = indent + 2
                while pos < len(tokens) and tokens[pos][0] == field_indent:
                    content = tokens[pos][1]
                    if ":" not in content:
                        raise DispatchError("frontmatter",
                                            f"malformed list-item field: {content!r}")
                    k2, _, v2 = content.partition(":")
                    if k2.strip() in mapping:
                        raise DispatchError("frontmatter",
                                            f"duplicate key {k2.strip()!r} in list item")
                    mapping[k2.strip()] = _scalar(v2)
                    pos += 1
                items.append(mapping)
            else:
                items.append(_scalar(_strip_unquoted_comment(rest)))
        return items, pos

    mapping: dict = {}
    while pos < len(tokens) and tokens[pos][0] == indent:
        content = tokens[pos][1]
        if ":" not in content:
            raise DispatchError("frontmatter", f"malformed frontmatter line: {content!r}")
        key, _, value = content.partition(":")
        key = key.strip()
        value = value.split(" #", 1)[0].rstrip()
        if key in mapping:
            raise DispatchError("frontmatter", f"duplicate key {key!r}")
        pos += 1
        stripped_value = value.strip()
        if stripped_value == "":
            nested, pos = _parse_block(tokens, pos, indent + 2)
            mapping[key] = nested if nested is not None else {}
        elif stripped_value == "{}":
            mapping[key] = {}
        elif stripped_value.startswith("[") and stripped_value.endswith("]"):
            mapping[key] = _split_inline_list(stripped_value)
        else:
            mapping[key] = _scalar(stripped_value)
    return mapping, pos


def parse_frontmatter(lines: list[str]) -> dict:
    """Parse the frontmatter body. Raises DispatchError on any malformed input."""
    tokens = _tokenize(lines)
    mapping, pos = _parse_block(tokens, 0, 0)
    if pos != len(tokens):
        raise DispatchError("frontmatter",
                            f"unexpected indentation at: {tokens[pos][1]!r}")
    if not isinstance(mapping, dict):
        raise DispatchError("frontmatter", "frontmatter body is not a mapping")
    return mapping


# --------------------------------------------------------------------------
# Grant path syntax
# --------------------------------------------------------------------------

_CONTROL_CHAR_RE = re.compile(r"[\x00-\x1f]")


def validate_path_entry(entry: object, key: str, failures: Failures):
    """Validate one repository-relative grant/exception path entry.

    Returns (ok, normalized). Supported syntax: an exact repository-relative
    path, or that path with a trailing '/**' recursive subtree marker. An
    empty path component — a doubled '/', or a leading or trailing '/' on
    the (non-recursive-marker) path — is rejected outright. It is never
    silently normalized away, because normalizing 'foo//bar' to 'foo/bar'
    would make the effective grant depend on a typo the Owner never wrote.
    """
    if not isinstance(entry, str) or not entry.strip():
        failures.add("grant", f"{key} has an empty or non-string entry ({entry!r})")
        return False, None
    text = entry.strip()
    if _CONTROL_CHAR_RE.search(text):
        failures.add("grant", f"{key} entry {entry!r} contains a control character")
        return False, None
    if "\\" in text:
        failures.add("grant", f"{key} entry {entry!r} contains a backslash")
        return False, None
    if text.startswith("~"):
        failures.add("grant", f"{key} entry {entry!r} uses home-directory expansion")
        return False, None

    recursive = text.endswith("/**")
    base = text[: -len("/**")] if recursive else text
    if "*" in base:
        failures.add("grant", f"{key} entry {entry!r} uses unsupported wildcard syntax")
        return False, None
    if base in ("", "/"):
        failures.add("grant", f"{key} entry {entry!r} is broader than the repository root")
        return False, None
    if base.startswith("/"):
        failures.add("grant", f"{key} entry {entry!r} is not repository-relative (absolute)")
        return False, None
    parts = base.split("/")
    if any(p == "" for p in parts):
        failures.add("grant",
                     f"{key} entry {entry!r} contains an empty path component (a doubled, "
                     "leading, or trailing '/'); it is rejected, never normalized")
        return False, None
    if ":" in parts[0]:
        failures.add("grant", f"{key} entry {entry!r} is not repository-relative "
                              "(carries a drive prefix)")
        return False, None
    if any(p in (".", "..") for p in parts):
        failures.add("grant", f"{key} entry {entry!r} contains '.' or '..'")
        return False, None

    normalized = "/".join(parts) + ("/**" if recursive else "")
    return True, normalized


KNOWN_GRANT_KEYS = frozenset({"filesystem.write", "filesystem.read.deny", *CAPABILITY_KEYS})


def validate_grant(grant: dict, failures: Failures) -> dict:
    """Validate grant.* and return a normalized copy (unique, sorted paths).

    An unrecognized top-level key (a likely capability typo, e.g.
    'shell.exec' instead of 'shell.execute') is rejected rather than
    silently ignored, so a misspelled capability never passes as if it were
    absent.
    """
    normalized: dict = {}

    for key in grant:
        if key not in KNOWN_GRANT_KEYS:
            failures.add("grant", f"grant has an unknown key {key!r}; supported keys are "
                                  f"{', '.join(sorted(KNOWN_GRANT_KEYS))}")

    write_entries = grant.get("filesystem.write")
    if write_entries is None:
        failures.add("grant", "filesystem.write is absent")
        normalized["filesystem.write"] = []
    elif not isinstance(write_entries, list):
        failures.add("grant", "filesystem.write is not a list")
        normalized["filesystem.write"] = []
    elif not write_entries:
        failures.add("grant", "filesystem.write is empty")
        normalized["filesystem.write"] = []
    else:
        seen: list[str] = []
        for entry in write_entries:
            ok, norm = validate_path_entry(entry, "filesystem.write", failures)
            if ok:
                if norm in seen:
                    failures.add("grant", f"filesystem.write has duplicate entry {norm!r}")
                else:
                    seen.append(norm)
        normalized["filesystem.write"] = seen

    deny_entries = grant.get("filesystem.read.deny")
    if deny_entries is None:
        normalized["filesystem.read.deny"] = []
    elif not isinstance(deny_entries, list):
        failures.add("grant", "filesystem.read.deny is not a list")
        normalized["filesystem.read.deny"] = []
    else:
        seen = []
        for entry in deny_entries:
            ok, norm = validate_path_entry(entry, "filesystem.read.deny", failures)
            if ok:
                if norm in seen:
                    failures.add("grant", f"filesystem.read.deny has duplicate entry {norm!r}")
                else:
                    seen.append(norm)
        normalized["filesystem.read.deny"] = seen

    for key in CAPABILITY_KEYS:
        if key not in grant:
            continue
        value = grant[key]
        allowed = CAPABILITY_VALUES[key]
        if not isinstance(value, str) or value not in allowed:
            failures.add("grant",
                         f"{key} has unsupported value {value!r}; expected one of "
                         f"{', '.join(allowed)}")
            continue
        normalized[key] = value

    return normalized


def runtime_contract(fields: dict, failures: Failures,
                     work_order_relpath: str | None = None) -> dict:
    """Normalize the grant subset consumed independently by the runtime wall."""
    grant = fields.get("grant")
    if not isinstance(grant, dict):
        failures.add("grant", "grant is not a mapping")
        grant = {}
    normalized = validate_grant(grant, failures)
    status = fields.get("status")
    if status != "ACTIVE":
        failures.add("frontmatter", "runtime status must be exactly 'ACTIVE'")
    return {
        "status": status,
        "filesystem.write": normalized.get("filesystem.write", []),
        "filesystem.read.deny": normalized.get("filesystem.read.deny", []),
        "shell.execute": normalized.get("shell.execute"),
        "network.egress": normalized.get("network.egress"),
        "protected_control_plane": sorted(control_plane_targets(work_order_relpath)),
    }


def validate_manifest_classification(fields: dict, declared_grant: dict,
                                     failures: Failures) -> None:
    """Validate Appendix B enforcement-classification fields."""
    enforced_by = fields.get("enforced_by")
    if "enforced_by" not in fields:
        failures.add("manifest", "missing required field 'enforced_by'")
    elif not isinstance(enforced_by, dict):
        failures.add("manifest", "enforced_by is not a mapping")
    else:
        for surface, mechanism in enforced_by.items():
            valid_scalar = isinstance(mechanism, str) and bool(mechanism.strip())
            valid_list = (isinstance(mechanism, list) and bool(mechanism)
                          and all(isinstance(item, str) and item.strip()
                                  for item in mechanism))
            if not (valid_scalar or valid_list):
                failures.add("manifest",
                             f"enforced_by surface {surface!r} has no non-empty "
                             "mechanism name")

    unenforced = fields.get("unenforced_boundaries")
    if "unenforced_boundaries" not in fields:
        failures.add("manifest", "missing required field 'unenforced_boundaries'")
    elif not isinstance(unenforced, list):
        failures.add("manifest", "unenforced_boundaries is not a list")
    else:
        declared = set(declared_grant)
        seen: set[str] = set()
        for surface in unenforced:
            if not isinstance(surface, str) or not surface.strip():
                failures.add("manifest",
                             f"unenforced_boundaries has an empty or non-string "
                             f"surface ({surface!r})")
                continue
            name = surface.strip()
            if name in seen:
                failures.add("manifest",
                             f"unenforced_boundaries has duplicate surface {name!r}")
            seen.add(name)
            if name not in declared:
                failures.add("manifest",
                             f"unenforced_boundaries classifies undeclared surface {name!r}")
        enforced_names = set(enforced_by.keys()) if isinstance(enforced_by, dict) else set()
        for name in sorted(enforced_names - declared):
            failures.add("manifest",
                         f"enforced_by classifies undeclared surface {name!r}")
        for name in sorted(enforced_names & seen):
            failures.add("manifest",
                         f"surface {name!r} is classified in both enforced_by and "
                         "unenforced_boundaries")
        for name in sorted(declared - enforced_names - seen):
            failures.add("manifest",
                         f"declared grant surface {name!r} is unclassified; list it exactly "
                         "once in enforced_by or unenforced_boundaries")


_EXCEPTION_SEGMENT_LITERAL_RE = re.compile(r"^[A-Za-z0-9_.\-]+$")
_EXCEPTION_SEGMENT_GLOB_RE = re.compile(r"^[A-Za-z0-9_.\-]*\*[A-Za-z0-9_.\-]*$")


def validate_exception_path(entry: object, failures: Failures):
    """Validate one dispatch_validation.prose_path_exceptions path.

    Deliberately more permissive than validate_path_entry(): these entries
    exist to classify residue-probe and traversal-glob patterns such as
    '**/__pycache__/**' and '**/*.pyc', which grant.filesystem.write and
    grant.filesystem.read.deny do not support and must not gain write
    authority from. Each '/'-separated segment must be a literal
    component, exactly '**', or a single-'*' glob within one segment
    (e.g. '*.pyc'). '.' and '..' segments, absolute paths, drive
    prefixes, backslashes, control characters, and home-directory
    expansion are rejected exactly as for grant paths.
    """
    key = "dispatch_validation.prose_path_exceptions"
    if not isinstance(entry, str) or not entry.strip():
        failures.add("grant", f"{key} has an empty or non-string entry ({entry!r})")
        return False, None
    text = entry.strip()
    if _CONTROL_CHAR_RE.search(text):
        failures.add("grant", f"{key} entry {entry!r} contains a control character")
        return False, None
    if "\\" in text:
        failures.add("grant", f"{key} entry {entry!r} contains a backslash")
        return False, None
    if text.startswith("~"):
        failures.add("grant", f"{key} entry {entry!r} uses home-directory expansion")
        return False, None
    if text.startswith("/"):
        failures.add("grant", f"{key} entry {entry!r} is not repository-relative (absolute)")
        return False, None

    parts = text.split("/")
    if any(p == "" for p in parts):
        failures.add("grant", f"{key} entry {entry!r} contains an empty path segment")
        return False, None
    if ":" in parts[0]:
        failures.add("grant", f"{key} entry {entry!r} is not repository-relative "
                              "(carries a drive prefix)")
        return False, None
    for part in parts:
        if part in (".", ".."):
            failures.add("grant", f"{key} entry {entry!r} contains '.' or '..'")
            return False, None
        if part == "**":
            continue
        if _EXCEPTION_SEGMENT_LITERAL_RE.match(part):
            continue
        if part.count("*") == 1 and _EXCEPTION_SEGMENT_GLOB_RE.match(part):
            continue
        failures.add("grant",
                     f"{key} entry {entry!r} uses unsupported wildcard syntax in "
                     f"segment {part!r}")
        return False, None
    return True, text


# --------------------------------------------------------------------------
# Protected control plane (Doctrine 8.7). Applies only to non-legacy
# (0.8+) candidates; see is_legacy_boundaries_revision above (DC.4).
# --------------------------------------------------------------------------

CONTROL_PLANE_STATIC_RELPATHS = frozenset({
    "/".join(POINTER_RELPATH),
    ".claude/hooks/wo_capability_wall.py",
    ".claude/settings.json",
    ".claude/settings.local.json",
    "governance/LOG-denials.jsonl",
})
CONTROL_PLANE_STATIC_SCOPES = frozenset({".claude/hooks/**"})

INSTRUMENT_KIND_BIRTH_TEST = "birth-test"
KNOWN_INSTRUMENT_KINDS = frozenset({INSTRUMENT_KIND_BIRTH_TEST})
PROBE_ROLE = "control_plane_falsification_probe"
KNOWN_PROBE_ENTRY_KEYS = frozenset({"path", "role"})


def _write_covers(write_entries: list[str], target: str) -> bool:
    """True if a normalized filesystem.write list authorizes mutating target,
    either by an exact entry or by a recursive '/**' ancestor entry."""
    if target in write_entries:
        return True
    for entry in write_entries:
        if entry.endswith("/**"):
            prefix = entry[: -len("/**")]
            if target == prefix or target.startswith(prefix + "/"):
                return True
    return False


def control_plane_targets(candidate_relpath: str | None) -> frozenset[str]:
    """The control-plane artifacts (Doctrine 8.7.1) relevant to one candidate:
    the fixed control-plane paths, plus the candidate's own path — a work
    order's or birth-test instrument's own frontmatter and body is itself a
    control-plane artifact. Scoped to grant.filesystem.write, the only grant
    surface with path granularity; shell/git/network surfaces have no
    path-level authority for this checker to inspect (Doctrine 8.3.3)."""
    targets = set(CONTROL_PLANE_STATIC_RELPATHS | CONTROL_PLANE_STATIC_SCOPES)
    if candidate_relpath is not None:
        targets.add(candidate_relpath)
    return frozenset(targets)


def _is_control_plane_path(path: str, candidate_relpath: str | None) -> bool:
    if path in control_plane_targets(candidate_relpath):
        return True
    for scope in CONTROL_PLANE_STATIC_SCOPES:
        prefix = scope[: -len("/**")]
        if path == prefix or path.startswith(prefix + "/"):
            return True
    return False


def _write_overlaps_scope(write_entries: list[str], scope: str,
                          labeled_exact_probes: set[str] | None = None) -> bool:
    """True when write authority reaches a protected recursive scope beyond
    exact probe paths that a birth-test instrument labels individually.

    An exact descendant such as the installed hook file does not authorize the
    whole hooks subtree. Treating it as though it did made the required exact
    birth-test probe impossible: wildcard probes are deliberately invalid.
    """
    prefix = scope[: -len("/**")]
    labeled = labeled_exact_probes or set()
    for entry in write_entries:
        recursive = entry.endswith("/**")
        entry_prefix = entry[: -len("/**")] if recursive else entry
        if not recursive and entry in labeled:
            continue
        if recursive and (entry_prefix == prefix
                          or entry_prefix.startswith(prefix + "/")
                          or prefix.startswith(entry_prefix + "/")):
            return True
        if not recursive and (entry_prefix == prefix
                              or entry_prefix.startswith(prefix + "/")):
            return True
    return False


def validate_control_plane(fields: dict, normalized_grant: dict,
                           candidate_relpath: str | None,
                           failures: Failures) -> list[dict]:
    """Doctrine 8.7.4.1-8.7.4.3. An ordinary candidate may never cover a
    control-plane path in grant.filesystem.write. A birth-test instrument may
    name an exact control-plane path solely as a labeled falsification probe,
    which confers no authority under 8.7.2 and must still be denied by the
    runtime wall. Returns the validated probe-entry list for rendering.
    """
    instrument_kind = fields.get("instrument_kind")
    is_birth_test = False
    if instrument_kind is not None:
        if instrument_kind not in KNOWN_INSTRUMENT_KINDS:
            failures.add("control-plane",
                         f"instrument_kind {instrument_kind!r} is not recognized; the only "
                         f"supported value is {INSTRUMENT_KIND_BIRTH_TEST!r}")
        else:
            is_birth_test = True

    probes = fields.get("control_plane_probes")
    validated_probes: list[dict] = []
    matched_paths: set[str] = set()
    if probes is not None:
        if not is_birth_test:
            failures.add("control-plane",
                         "control_plane_probes is declared but instrument_kind is not "
                         f"{INSTRUMENT_KIND_BIRTH_TEST!r}; only a birth-test instrument may "
                         "label a control-plane falsification probe")
        if not isinstance(probes, list) or not probes:
            failures.add("control-plane", "control_plane_probes is not a non-empty list")
        else:
            targets = control_plane_targets(candidate_relpath)
            seen_paths: list[str] = []
            for entry in probes:
                if not isinstance(entry, dict):
                    failures.add("control-plane",
                                 f"control_plane_probes entry {entry!r} is not a mapping")
                    continue
                for key in entry:
                    if key not in KNOWN_PROBE_ENTRY_KEYS:
                        failures.add("control-plane",
                                     f"control_plane_probes entry has an unknown key {key!r}")
                path = entry.get("path")
                role = entry.get("role")
                if not isinstance(path, str) or not path.strip():
                    failures.add("control-plane",
                                 "control_plane_probes entry is missing a string 'path'")
                    continue
                if path.endswith("/**") or "*" in path:
                    failures.add("control-plane",
                                 f"control_plane_probes entry {path!r} is not an exact, "
                                 "non-wildcard path")
                    continue
                if path in seen_paths:
                    failures.add("control-plane",
                                 f"control_plane_probes has duplicate entry {path!r}")
                    continue
                seen_paths.append(path)
                if role != PROBE_ROLE:
                    failures.add("control-plane",
                                 f"control_plane_probes entry for {path!r} has role {role!r}; "
                                 f"expected exactly {PROBE_ROLE!r}")
                    continue
                if not _is_control_plane_path(path, candidate_relpath):
                    failures.add("control-plane",
                                 f"control_plane_probes entry {path!r} does not name a "
                                 "recognized control-plane path (Doctrine 8.7.1)")
                    continue
                write_entries = normalized_grant.get("filesystem.write") or []
                if not _write_covers(write_entries, path):
                    failures.add("control-plane",
                                 f"control_plane_probes entry {path!r} does not match any "
                                 "grant.filesystem.write target")
                    continue
                matched_paths.add(path)
                validated_probes.append({"path": path, "role": role})

    write_entries = normalized_grant.get("filesystem.write") or []
    for target in sorted(control_plane_targets(candidate_relpath)):
        covered = (_write_overlaps_scope(
                       write_entries, target,
                       matched_paths if is_birth_test else None)
                   if target in CONTROL_PLANE_STATIC_SCOPES
                   else _write_covers(write_entries, target))
        if not covered:
            continue
        if is_birth_test and target in matched_paths:
            continue
        if is_birth_test:
            failures.add("control-plane",
                         f"grant.filesystem.write covers control-plane path {target!r} but it "
                         "is not labeled in control_plane_probes (Doctrine 8.7.4.2); no "
                         "control-plane path may be left unlabeled")
        else:
            failures.add("control-plane",
                         f"grant.filesystem.write covers control-plane path {target!r}; an "
                         "ordinary work order may never claim mutation authority over a "
                         "control-plane artifact (Doctrine 8.7.2). Declare "
                         f"instrument_kind: {INSTRUMENT_KIND_BIRTH_TEST!r} and label it under "
                         "control_plane_probes to exercise it as a birth-test falsification "
                         "probe (Doctrine 8.7.4)")

    return validated_probes


KNOWN_DISPATCH_VALIDATION_KEYS = frozenset({"prose_path_exceptions"})
KNOWN_EXCEPTION_ENTRY_KEYS = frozenset({"path", "role"})


def validate_exceptions(dispatch_validation: object, failures: Failures) -> list[dict]:
    if dispatch_validation is None:
        return []
    if not isinstance(dispatch_validation, dict):
        failures.add("grant", "dispatch_validation is not a mapping")
        return []
    for key in dispatch_validation:
        if key not in KNOWN_DISPATCH_VALIDATION_KEYS:
            failures.add("grant",
                         f"dispatch_validation has an unknown key {key!r}; supported keys "
                         f"are {', '.join(sorted(KNOWN_DISPATCH_VALIDATION_KEYS))}")
    entries = dispatch_validation.get("prose_path_exceptions")
    if entries is None:
        return []
    if not isinstance(entries, list):
        failures.add("grant", "dispatch_validation.prose_path_exceptions is not a list")
        return []
    result = []
    seen_paths: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or "path" not in entry or "role" not in entry:
            failures.add("grant",
                         f"dispatch_validation.prose_path_exceptions entry {entry!r} "
                         "must carry both 'path' and 'role'")
            continue
        extra_keys = set(entry) - KNOWN_EXCEPTION_ENTRY_KEYS
        if extra_keys:
            failures.add("grant",
                         "dispatch_validation.prose_path_exceptions entry has unknown "
                         f"key(s) {sorted(extra_keys)!r}; supported keys are "
                         f"{', '.join(sorted(KNOWN_EXCEPTION_ENTRY_KEYS))}")
            continue
        ok, norm = validate_exception_path(entry["path"], failures)
        role = entry["role"]
        if not isinstance(role, str) or not role.strip():
            failures.add("grant",
                         f"dispatch_validation.prose_path_exceptions entry for "
                         f"{entry.get('path')!r} has an empty role")
            continue
        if not ok:
            continue
        if norm in seen_paths:
            failures.add("grant",
                         f"dispatch_validation.prose_path_exceptions has duplicate path {norm!r}")
            continue
        seen_paths.append(norm)
        result.append({"path": norm, "role": role.strip()})
    return result


# --------------------------------------------------------------------------
# Identity: id, status, doctrine_rev
# --------------------------------------------------------------------------

def validate_identity(fields: dict, path: Path, repo_root: Path,
                      require_active: bool, failures: Failures) -> None:
    for name in REQUIRED_TOP_FIELDS:
        if name not in fields:
            failures.add("frontmatter", f"missing required field {name!r}")

    wo_id = fields.get("id")
    if wo_id is not None:
        if not isinstance(wo_id, str) or not ID_RE.match(wo_id):
            failures.add("frontmatter",
                         f"id {wo_id!r} does not match WO-NNN or "
                         "WO-<UPPERCASE-NAMESPACE>-NNN")
        elif (path.name != f"{wo_id}.md"
              and not path.name.startswith(f"{wo_id}-")):
            failures.add("frontmatter",
                         f"filename {path.name!r} does not match id {wo_id!r} "
                         "as an exact Markdown filename or hyphen-delimited prefix")

    status = fields.get("status")
    if require_active and status != "ACTIVE":
        failures.add("frontmatter", f"status is {status!r}, expected exactly 'ACTIVE'")
    retirement_fields = sorted({"void", "superseded_by"} & set(fields))
    if require_active and retirement_fields:
        failures.add(
            "frontmatter",
            "an ACTIVE work order cannot also carry retirement metadata: "
            + ", ".join(retirement_fields))

    doctrine_rev = fields.get("doctrine_rev")
    if "doctrine_rev" in fields:
        # Doctrine DC.4: a project's bound revision is a fact the project's
        # Owner records and controls, independent of the methodology-source
        # repository's own current revision. Root DOCTRINE.md, when present,
        # is never read to infer or check that binding.
        if not isinstance(doctrine_rev, str) or not doctrine_rev.strip():
            failures.add("frontmatter",
                         f"doctrine_rev {doctrine_rev!r} is not a non-empty string")


# --------------------------------------------------------------------------
# Path-shaped prose-token scan (B.3 / B.4)
# --------------------------------------------------------------------------

BACKTICK_TOKEN_RE = re.compile(r"`([^`]+)`")
PATH_TOKEN_CHARSET_RE = re.compile(r"^[A-Za-z0-9_.\-/*]+$")


_PATH_SEGMENT_LITERAL_RE = re.compile(r"^\.?[A-Za-z0-9_\-]+(\.[A-Za-z0-9_\-]+)*$")


def _plausible_path_segment(part: str) -> bool:
    """True when `part` is shaped like a real path component or a '.'/'..'
    traversal marker.

    A traversal marker ('.' or '..') counts as plausible on purpose: such a
    token must still be scanned and force-flagged (see check_prose_paths),
    not silently excluded from consideration by the tokenizer. What this
    function excludes is content that merely contains a stray '..'
    substring without being segment-shaped at all, such as a git ref/range
    expression like 'main...HEAD' — three consecutive dots is not a
    plausible filename and is not a traversal marker either, so a token
    built from it is not path-shaped in the first place.
    """
    if part in (".", ".."):
        return True
    if part == "**":
        return True
    if part.count("*") == 1:
        return bool(re.match(r"^[A-Za-z0-9_.\-]*$", part.replace("*", "", 1)))
    return bool(_PATH_SEGMENT_LITERAL_RE.match(part))


def path_shaped_tokens(section_text: str) -> list[str]:
    tokens = []
    for match in BACKTICK_TOKEN_RE.finditer(section_text):
        token = match.group(1)
        if "/" not in token:
            continue
        if not PATH_TOKEN_CHARSET_RE.match(token):
            continue
        parts = token.split("/")
        if any(p == "" for p in parts):
            continue
        if not all(_plausible_path_segment(p) for p in parts):
            continue
        tokens.append(token)
    return tokens


def _has_traversal_segment(token: str) -> bool:
    return any(part in (".", "..") for part in token.split("/"))


def extract_sections(text: str, heading_prefix: str) -> list[str]:
    """Return every same-prefixed level-two section in document order."""
    lines = text.splitlines()
    sections: list[str] = []
    index = 0
    while index < len(lines):
        if lines[index].strip().startswith(heading_prefix):
            start = index
            end = len(lines)
            for cursor in range(start + 1, len(lines)):
                if lines[cursor].strip().startswith("## "):
                    end = cursor
                    break
            sections.append("\n".join(lines[start:end]))
            index = end
        else:
            index += 1
    return sections


def _token_resolved(token: str, resolved: set) -> bool:
    """True when `token` names the same path a resolved entry covers.

    Exact match is the primary rule. A token may also drop the trailing
    '/**' recursive-subtree marker a grant/exception entry carries (prose
    commonly says "`dist/`" where the grant says `dist/**`); the reverse
    (a token that already ends in a bare '/') is normalized the same way.
    This does not widen resolution to a different base path, only to the
    same base path spelled with or without its recursive marker.
    """
    if token in resolved:
        return True
    stripped = token.rstrip("/")
    if stripped in resolved:
        return True
    if f"{stripped}/**" in resolved:
        return True
    return False


def check_prose_paths(text: str, normalized_grant: dict, exceptions: list[dict],
                      failures: Failures) -> None:
    resolved = set(normalized_grant.get("filesystem.write") or [])
    resolved |= set(normalized_grant.get("filesystem.read.deny") or [])
    resolved |= {entry["path"] for entry in exceptions}

    for label, prefix in (("B.3", "## B.3"), ("B.4", "## B.4")):
        for section in extract_sections(text, prefix):
            for token in path_shaped_tokens(section):
                if _has_traversal_segment(token):
                    failures.add("prose-path",
                                 f"{label} token {token!r} contains a '.' or '..' path segment "
                                 "and can never be grant-resolved (prose_path_out_of_grant)")
                    continue
                if not _token_resolved(token, resolved):
                    failures.add("prose-path",
                                 f"{label} token {token!r} is not resolved by "
                                 "filesystem.write, filesystem.read.deny, or a typed "
                                 "prose_path_exceptions entry (prose_path_out_of_grant)")


# --------------------------------------------------------------------------
# Generated boundaries (Doctrine Appendix B; B.4 under 0.6/0.7, B.7 under 0.8+)
# --------------------------------------------------------------------------

# DC.4 project-binding compatibility: a candidate's doctrine_rev is the
# project's own bound revision, independent of this methodology repository's
# current revision. Revisions ratified before Doctrine 0.8 never had a B.7 or
# a protected-control-plane rule, so a 0.6/0.7 candidate is rendered and
# validated exactly as it always was; only 0.8+ gets the new heading and the
# instrument_kind/control_plane_probes schema.
LEGACY_BOUNDARIES_REVISIONS = frozenset({"0.6", "0.7"})
LEGACY_BOUNDARIES_HEADING = "## B.4 Generated boundaries"
CURRENT_BOUNDARIES_HEADING = "## B.7 Generated boundaries"
BOUNDARIES_HEADING = LEGACY_BOUNDARIES_HEADING  # default/back-compat for direct callers


def boundaries_heading_for_revision(doctrine_rev: object) -> str:
    if isinstance(doctrine_rev, str) and doctrine_rev in LEGACY_BOUNDARIES_REVISIONS:
        return LEGACY_BOUNDARIES_HEADING
    return CURRENT_BOUNDARIES_HEADING


def is_legacy_boundaries_revision(doctrine_rev: object) -> bool:
    return isinstance(doctrine_rev, str) and doctrine_rev in LEGACY_BOUNDARIES_REVISIONS


BOUNDARIES_INTRO = (
    "This block is the Owner-supplied seed rendering for the first implementation of",
    "the generator. The accepted checker must reproduce it byte-for-byte solely from",
    "frontmatter; thereafter Owners replace this block only with checker output.",
)
BOUNDARIES_CLOSING = (
    "This checker is read-only. It does not repair, create or remove the activation",
    "pointer, mutate a work order, retrieve closed history, modify adopter templates,",
    "access another project, install packages, use the network, commit, push, tag,",
    "publish, select a license, or change repository visibility.",
)
BEGIN_MARKER = "<!-- BEGIN GENERATED BOUNDARIES -->"
END_MARKER = "<!-- END GENERATED BOUNDARIES -->"


def render_boundary_lines(normalized_grant: dict, exceptions: list[dict],
                          control_plane_probes: list[dict] | None = None,
                          heading: str = BOUNDARIES_HEADING) -> list[str]:
    lines: list[str] = [heading, ""]
    lines.extend(BOUNDARIES_INTRO)
    lines.append("")
    lines.append("### Writable repository paths")
    lines.append("")
    for entry in normalized_grant.get("filesystem.write") or []:
        lines.append(f"- `{entry}`")
    lines.append("")
    lines.append("### Read-denied repository paths")
    lines.append("")
    for entry in normalized_grant.get("filesystem.read.deny") or []:
        lines.append(f"- `{entry}`")
    lines.append("")
    lines.append("### Other capability limits")
    lines.append("")
    for key in CAPABILITY_KEYS:
        if key in normalized_grant:
            lines.append(f"- {key}: `{normalized_grant[key]}`")
    lines.append("")
    lines.append("### Typed non-write path exceptions")
    lines.append("")
    for entry in exceptions:
        lines.append(f"- `{entry['path']}` — `{entry['role']}`")
    lines.append("")
    if heading == CURRENT_BOUNDARIES_HEADING:
        # Doctrine 8.7.4.2: rendered only for the current (0.8+) heading, so
        # a 0.6/0.7 candidate's byte-for-byte rendering is unchanged.
        lines.append(
            "### Control-plane falsification probes (expected-denial; confer no authority)")
        lines.append("")
        for entry in sorted((control_plane_probes or []), key=lambda e: e.get("path", "")):
            lines.append(f"- `{entry.get('path')}` — `{entry.get('role')}` "
                         "(Doctrine 8.7.4: expected-denial probe, confers no authority)")
        lines.append("")
    lines.extend(BOUNDARIES_CLOSING)
    return lines


def extract_generated_block(text: str) -> list[str] | None:
    lines = text.splitlines()
    try:
        start = lines.index(BEGIN_MARKER)
        end = lines.index(END_MARKER)
    except ValueError:
        return None
    if end <= start:
        return None
    return lines[start + 1: end]


def check_boundaries_generated(text: str, normalized_grant: dict, exceptions: list[dict],
                               failures: Failures,
                               control_plane_probes: list[dict] | None = None,
                               heading: str = BOUNDARIES_HEADING) -> None:
    actual = extract_generated_block(text)
    if actual is None:
        failures.add("boundaries",
                     "no BEGIN/END GENERATED BOUNDARIES markers found in the work order")
        return
    expected = render_boundary_lines(normalized_grant, exceptions, control_plane_probes, heading)
    if actual != expected:
        failures.add("boundaries",
                     "boundaries_not_generated: the issued generated-boundaries block differs "
                     "from the frontmatter-derived rendering")


# --------------------------------------------------------------------------
# Candidate: full validation of one work-order file's bytes and frontmatter
# --------------------------------------------------------------------------

def validate_candidate(path: Path, repo_root: Path, require_active: bool,
                       failures: Failures):
    """Validate one work order's bytes and frontmatter.

    Returns (fields, normalized_grant, exceptions) for further use (boundaries
    comparison, prose-path scan), or (None, None, None) if bytes/frontmatter
    could not be parsed at all.
    """
    text = load_work_order_text(path, failures)
    if text is None:
        return None, None, None

    if repo_root / "governance" / "work-orders" not in path.resolve().parents:
        failures.add("bytes", f"{path} does not lie under governance/work-orders/")

    body = frontmatter_slice(text, failures)
    if body is None:
        return None, None, None
    try:
        fields = parse_frontmatter(body)
    except DispatchError as exc:
        failures.add(exc.category, exc.detail)
        return None, None, None

    validate_identity(fields, path, repo_root, require_active, failures)

    grant = fields.get("grant")
    if not isinstance(grant, dict):
        failures.add("grant", "grant is missing or not a mapping")
        grant = {}
    normalized_grant = validate_grant(grant, failures)
    validate_manifest_classification(fields, grant, failures)

    exceptions = validate_exceptions(fields.get("dispatch_validation"), failures)

    doctrine_rev = fields.get("doctrine_rev")
    heading = boundaries_heading_for_revision(doctrine_rev)
    validated_probes: list[dict] = []
    if not is_legacy_boundaries_revision(doctrine_rev):
        candidate_relpath = None
        try:
            candidate_relpath = path.resolve().relative_to(repo_root.resolve()).as_posix()
        except (OSError, ValueError):
            pass
        validated_probes = validate_control_plane(fields, normalized_grant,
                                                   candidate_relpath, failures)

    check_boundaries_generated(text, normalized_grant, exceptions, failures,
                               validated_probes, heading)
    check_prose_paths(text, normalized_grant, exceptions, failures)

    return fields, normalized_grant, exceptions


def print_effective_grant(fields: dict, normalized_grant: dict, exceptions: list[dict],
                          candidate_relpath: str | None = None) -> None:
    import hashlib
    doctrine_rev = fields.get("doctrine_rev")
    heading = boundaries_heading_for_revision(doctrine_rev)
    probes: list[dict] = []
    if not is_legacy_boundaries_revision(doctrine_rev):
        probes = validate_control_plane(fields, normalized_grant, candidate_relpath, Failures())
    lines = render_boundary_lines(normalized_grant, exceptions, probes, heading)
    digest = hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()
    print("effective grant (normalized):")
    for line in lines:
        print(f"  {line}")
    print(f"effective grant SHA-256: {digest}")


# --------------------------------------------------------------------------
# Modes
# --------------------------------------------------------------------------

def run_lockout(repo_root: Path, allow: list[str]) -> Failures:
    failures = Failures()
    check_git_baseline(repo_root, failures)
    pointer_file = repo_root.joinpath(*POINTER_RELPATH)
    if pointer_file.is_file():
        failures.add("lockout", ".claude/active-wo.txt exists; this is not a lockout state")
    siblings = pointer_extension_siblings(repo_root)
    for name in siblings:
        failures.add("pointer",
                     f".claude/{name} looks like a misnamed activation pointer "
                     "(expected exactly .claude/active-wo.txt)")
    check_dirty_tree(repo_root, LOCKOUT, allow, None, failures)
    check_residue(repo_root, failures)
    return failures


def resolve_work_order_arg(repo_root: Path, arg: str, failures: Failures) -> Path | None:
    """Resolve a --work-order / --emit-boundaries argument, or record why not.

    The public interface requires a repository-relative path under
    governance/work-orders/. An absolute path is rejected outright, even one
    that happens to resolve inside the repository — the interface is
    repository-relative by contract, not by coincidence of where it lands.
    The resolved target must exist, must not be reached through a symlink
    (nor any symlinked ancestor directory), and must match the on-disk name
    exactly, using the same exact_case_path() resolution the active pointer
    uses, so a candidate and an active work order are held to one standard.
    """
    if Path(arg).is_absolute():
        failures.add("path",
                     f"--work-order argument {arg!r} is an absolute path; a "
                     "repository-relative path under governance/work-orders/ is required, "
                     "even when the absolute path resolves inside the repository")
        return None
    parts = tuple(p for p in arg.replace("\\", "/").split("/") if p not in ("",))
    if any(p == ".." for p in parts):
        failures.add("path", f"--work-order argument {arg!r} escapes the repository with '..'")
        return None
    if parts[: len(WO_DIR_RELPATH)] != WO_DIR_RELPATH:
        failures.add("path",
                     f"--work-order argument {arg!r} does not resolve under "
                     f"{'/'.join(WO_DIR_RELPATH)}/")
        return None
    exact = exact_case_path(repo_root, parts)
    if exact is None:
        failures.add("path",
                     f"--work-order argument {arg!r} does not exist, is reached through a "
                     "symlink, or its case does not exactly match the name on disk")
        return None
    if exact.is_symlink():
        failures.add("path", f"--work-order argument {arg!r} is a symlink")
        return None
    return exact


def run_candidate(repo_root: Path, work_order_arg: str, allow: list[str]) -> Failures:
    failures = Failures()
    check_git_baseline(repo_root, failures)

    path = resolve_work_order_arg(repo_root, work_order_arg, failures)
    wo_relpath = None
    if path is not None:
        try:
            wo_relpath = path.resolve().relative_to(repo_root.resolve()).as_posix()
        except (OSError, ValueError):
            pass

    check_dirty_tree(repo_root, CANDIDATE, allow, wo_relpath, failures)
    check_residue(repo_root, failures)

    if path is not None:
        fields, normalized_grant, exceptions = validate_candidate(
            path, repo_root, require_active=True, failures=failures)
        if fields is not None:
            print_effective_grant(fields, normalized_grant, exceptions, wo_relpath)
    return failures


def run_active(repo_root: Path, allow: list[str]) -> Failures:
    failures = Failures()
    check_git_baseline(repo_root, failures)

    siblings = pointer_extension_siblings(repo_root)
    for name in siblings:
        failures.add("pointer",
                     f".claude/{name} looks like a misnamed activation pointer "
                     "(expected exactly .claude/active-wo.txt)")

    relpath = load_pointer(repo_root, failures)
    target = None
    if relpath is not None:
        target = resolve_active_target(repo_root, relpath, failures)

    wo_relpath = relpath if target is not None else None
    check_dirty_tree(repo_root, ACTIVE, allow, wo_relpath, failures)
    check_residue(repo_root, failures)

    if target is not None:
        fields, normalized_grant, exceptions = validate_candidate(
            target, repo_root, require_active=True, failures=failures)
        if fields is not None:
            print_effective_grant(fields, normalized_grant, exceptions, wo_relpath)
    return failures


def run_emit_boundaries(repo_root: Path, work_order_arg: str) -> tuple[Failures, str | None]:
    failures = Failures()
    path = resolve_work_order_arg(repo_root, work_order_arg, failures)
    if path is None:
        return failures, None
    text = load_work_order_text(path, failures)
    if text is None:
        return failures, None
    body = frontmatter_slice(text, failures)
    if body is None:
        return failures, None
    try:
        fields = parse_frontmatter(body)
    except DispatchError as exc:
        failures.add(exc.category, exc.detail)
        return failures, None
    grant = fields.get("grant")
    if not isinstance(grant, dict):
        failures.add("grant", "grant is missing or not a mapping")
        return failures, None
    normalized_grant = validate_grant(grant, failures)
    exceptions = validate_exceptions(fields.get("dispatch_validation"), failures)
    doctrine_rev = fields.get("doctrine_rev")
    heading = boundaries_heading_for_revision(doctrine_rev)
    probes: list[dict] = []
    if not is_legacy_boundaries_revision(doctrine_rev):
        candidate_relpath = None
        try:
            candidate_relpath = path.resolve().relative_to(repo_root.resolve()).as_posix()
        except (OSError, ValueError):
            pass
        probes = validate_control_plane(fields, normalized_grant, candidate_relpath, failures)
    if failures:
        return failures, None
    rendered = "\n".join(render_boundary_lines(normalized_grant, exceptions,
                                               probes, heading)) + "\n"
    return failures, rendered


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic pre-dispatch validator for Writwall work-order state.")
    parser.add_argument("--lockout", action="store_true",
                        help="validate the intentional between-work-order lockout state")
    parser.add_argument("--active", action="store_true",
                        help="validate the pointer and the work order it names")
    parser.add_argument("--work-order", metavar="PATH",
                        help="validate one candidate work-order file before pointer creation")
    parser.add_argument("--emit-boundaries", action="store_true",
                        help="print the canonical B.4 block derived from --work-order frontmatter")
    parser.add_argument("--allow", action="append", default=[],
                        metavar="REPO-RELATIVE-PATH",
                        help="explicit dispatch-time allowlist entry for the dirty-tree check "
                             "(repeatable; testable configuration, not a routine escape hatch)")
    return parser


def resolve_mode(args: argparse.Namespace):
    """Return (mode, error) — error is a (category, detail) tuple or None."""
    flags_set = sum([args.lockout, args.active, bool(args.work_order), args.emit_boundaries])
    if args.emit_boundaries:
        if not args.work_order or args.lockout or args.active:
            return None, ("mode", "--emit-boundaries requires exactly --work-order and no "
                                  "other mode flag")
        return EMIT, None
    if flags_set == 0:
        return None, ("mode", "no mode selected; specify exactly one of --lockout, --active, "
                              "--work-order, or --emit-boundaries with --work-order")
    if flags_set > 1:
        return None, ("mode", "conflicting modes selected; specify exactly one of --lockout, "
                              "--active, --work-order, or --emit-boundaries with --work-order")
    if args.lockout:
        return LOCKOUT, None
    if args.active:
        return ACTIVE, None
    return CANDIDATE, None


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    mode, error = resolve_mode(args)
    if error is not None:
        category, detail = error
        print(f"FAIL: 1 problem(s)\n\n  [{category}] {detail}")
        return 1

    repo_root = REPO_ROOT

    if mode == LOCKOUT:
        failures = run_lockout(repo_root, args.allow)
    elif mode == CANDIDATE:
        failures = run_candidate(repo_root, args.work_order, args.allow)
    elif mode == ACTIVE:
        failures = run_active(repo_root, args.allow)
    else:  # EMIT
        failures, rendered = run_emit_boundaries(repo_root, args.work_order)
        if not failures and rendered is not None:
            print(rendered, end="")
            return 0
        print(f"\nFAIL: {len(failures.items)} problem(s)\n")
        for item in failures.items:
            print(f"  {item}")
        return 1

    if failures:
        print(f"\nFAIL: {len(failures.items)} problem(s)\n")
        for item in failures.items:
            print(f"  {item}")
        return 1
    print(f"\nOK: {mode} state is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
