#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Build the Plumbline source distribution archive.

Standard library only. Produces exactly one ZIP containing exactly one
top-level directory, `plumbline/`. No nested archive, no loose duplicate
files alongside the canonical paths.

WHAT THIS ARCHIVE IS. `plumbline-<revision>.zip` is a source distribution, not
an overlay. It is not unpacked into an adopting project. It carries the
methodology, the templates, the adapters, the adoption routes, the checks, and
Plumbline's own operating charter as an inspectable self-hosting example
(Doctrine 5.1.4). An adopter instantiates only the project-side artifacts,
through the routes documented in ADOPTING.md.

Plumbline's own charter, governance directory, decisions, plan, state, work
history, and authority are working records under Doctrine 5.1.5. They ship so
that the example is readable and auditable. They are never copied into an
adopting project by any adoption route, and `checks/check_distribution.py`
fails if one appears inside the adoption skill's bundle.

Naming is governed by the doctrine's own change control (DC.3.5): while
DC.1 records a ratification candidate, the archive name must carry a
candidate marker. A final release name is permitted only when DC.1 records
`Ratified` and the DC.2 row for that revision records ratification.

Usage:
    python scripts/build_distribution.py --output dist/
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = "plumbline"
MANIFEST_NAME = "MANIFEST.sha256"

# Excluded from the distribution entirely.
EXCLUDED_DIR_NAMES = frozenset({
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".cache",
    "htmlcov",
    "dist",
    "bootstrap",
})

# Provider installation. Excluded entirely before adoption; after adoption the
# archive carries exactly these two files, because the portable installation is
# part of Plumbline's real self-hosted example (Owner disposition 2026-08-16).
# Everything else under .claude/ is machine-local and never ships.
CLAUDE_DIR = ".claude"
PACKAGED_CLAUDE_FILES = frozenset({
    ".claude/settings.json",
    ".claude/hooks/wo_capability_wall.py",
})
EXCLUDED_FILE_NAMES = frozenset({
    ".coverage",
})
# Per-work-order reports are named REMEDIATION-REPORT-WO-PL-00n.md, so these
# must match by prefix. An exact-name exclusion silently ships every report
# after the first.
EXCLUDED_FILE_PREFIXES = (
    "REMEDIATION-REPORT",
    "REMEDIATION-INVENTORY",
)
EXCLUDED_SUFFIXES = (".pyc", ".pyo", ".zip")

# --------------------------------------------------------------------------
# Governance packaging gate (Owner disposition, 2026-08-16)
#
# Plumbline's finalized self-hosted governance instance belongs in the public
# source distribution as a real working example. Unratified drafts do not.
#
#   pre-adoption : the whole governance/ subtree is excluded
#   adopted      : the finalized instance is included
#   contradictory: the build FAILS rather than ship a half-adopted state
# --------------------------------------------------------------------------
GOVERNANCE = "governance"
ADOPTION_RECORD = ("governance", "decisions", "DR-001.md")
PROPOSED_ADOPTION_RECORD = ("governance", "decisions", "DR-001-ADOPTION-PROPOSED.md")

# Never packaged in any state.
NEVER_PACKAGED_NAMES = frozenset({"DR-001-ADOPTION-PROPOSED.md"})

# --------------------------------------------------------------------------
# Proposed-status detection (RFI-14)
#
# A governed document declares its own status in one of two places: a
# top-level `status:` field in its opening frontmatter, or an explicit
# human-readable marker line near the top of the body.
#
# The earlier gate matched exactly one literal, `Status: PROPOSED`, inside a
# fixed 40-line window. Ordinary lowercase frontmatter, a quoted value, a
# different capitalization, and a frontmatter block longer than the window all
# evaded it, so a draft could reach an adopted archive. Detection is therefore
# semantic rather than literal:
#
#   * the complete opening frontmatter block is parsed, however long it is, so
#     no field position can hide from a window;
#   * a top-level `status:` field there is AUTHORITATIVE. A record declaring
#     ISSUED, ACTIVE, COMPLETE, RATIFIED, or RFI-BLOCKED is final even when its
#     body quotes the PROPOSED language it carried while it was a draft. That
#     quotation is history, not a status declaration, and a completed record
#     must not be forced to redact its own drafting history to ship;
#   * only when no such field exists does the bounded body scan apply, and it
#     matches a line that DECLARES a status rather than prose mentioning the
#     words "status" and "proposed". The line must begin with `status:` once
#     Markdown heading, emphasis, block-quote, and code decoration is stripped.
#
# This block is mirrored verbatim in checks/check_distribution.py. The builder
# and the checker must agree on every document or the gate is theatre.
# --------------------------------------------------------------------------
STATUS_SCAN_LINES = 40
FRONTMATTER_FENCES = ("---", "...")
MARKER_DECORATION = "#>*_` \t"
STATUS_FIELD_RE = re.compile(r"^status\s*:\s*(.*)$", re.IGNORECASE)
PROPOSED_VALUE_RE = re.compile(r"^[\s'\"`*_]*proposed\b", re.IGNORECASE)

PRE_ADOPTION = "pre-adoption"
ADOPTED = "adopted"

# --------------------------------------------------------------------------
# Transient release state (WO-PL-015)
#
# A release candidate represents a between-work-order checkpoint, never an
# in-progress implementation envelope. Three artifacts mark live work in
# progress: the activation pointer, any regular file under the live
# work-order directory, and any regular file under the live report
# directory. `checks/check_distribution.py` consumes this same definition
# rather than restating it, and the same relative-path rule applies to an
# archive member name once its `plumbline/` archive root is stripped.
#
# The two tracked root `.gitkeep` placeholders are not transient: they are
# the directory's own tracked presence, not live work. Only those two EXACT
# relative paths are exempt. A `.gitkeep` nested under a subdirectory is not
# a tracked repository placeholder — nothing in this repository tracks one —
# so it is ordinary transient content, exactly like any other file placed
# under a live directory during a work order.
# --------------------------------------------------------------------------

ACTIVATION_POINTER = ".claude/active-wo.txt"
LIVE_WORK_ORDER_DIR = "governance/work-orders"
LIVE_REPORT_DIR = "governance/reports"
LIVE_STATE_DIRS = (LIVE_WORK_ORDER_DIR, LIVE_REPORT_DIR)
TRACKED_PLACEHOLDERS = frozenset(
    f"{live_dir}/.gitkeep" for live_dir in LIVE_STATE_DIRS)


class TransientReleaseStateError(SystemExit):
    """Raised to fail the build while transient live-work state is present."""


def is_transient_release_path(relative: str) -> bool:
    """True for a relative POSIX path that names transient live-work state.

    Applies identically to a working-tree path relative to the repository
    root and to an archive member name relative to `plumbline/`.
    """
    if relative == ACTIVATION_POINTER:
        return True
    if relative in TRACKED_PLACEHOLDERS:
        return False
    for live_dir in LIVE_STATE_DIRS:
        prefix = live_dir + "/"
        if relative.startswith(prefix) and relative != prefix:
            return True
    return False


def transient_release_paths(repo_root: Path = REPO_ROOT) -> list[str]:
    """Every transient live-work path actually present, sorted."""
    found = []
    pointer = repo_root / ACTIVATION_POINTER
    if pointer.is_file():
        found.append(ACTIVATION_POINTER)
    for live_dir in LIVE_STATE_DIRS:
        directory = repo_root / live_dir
        if not directory.is_dir():
            continue
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(repo_root).as_posix()
            if is_transient_release_path(relative):
                found.append(relative)
    return sorted(found)


def transient_release_preflight(repo_root: Path = REPO_ROOT) -> None:
    """Refuse to build while any transient live-work state is present."""
    found = transient_release_paths(repo_root)
    if found:
        raise TransientReleaseStateError(
            "build refused: transient live-work state is present. A release "
            "candidate is a between-work-order checkpoint, never an "
            "in-progress implementation envelope. Close out the active work "
            "order (or clear the pointer and live directories) before "
            "building.\n  " + "\n  ".join(found))


class GovernanceStateError(SystemExit):
    """Raised to fail the build on a contradictory governance state."""


def frontmatter_body(lines: list[str]) -> list[str] | None:
    """The lines inside an opening `---` frontmatter block, or None."""
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() in FRONTMATTER_FENCES:
            return lines[1:index]
    return None


def scalar_value(raw: str) -> str:
    """A YAML scalar with any unquoted trailing comment removed."""
    value = raw.strip()
    if value[:1] not in ("'", '"'):
        for comment in (" #", "\t#"):
            value = value.split(comment, 1)[0]
    return value.strip()


def declared_status(lines: list[str]) -> str | None:
    """The top-level `status:` value in the opening frontmatter, or None."""
    body = frontmatter_body(lines)
    if body is None:
        return None
    for line in body:
        if line[:1] in (" ", "\t"):
            continue                    # a nested key, not a top-level field
        match = STATUS_FIELD_RE.match(line)
        if match:
            return scalar_value(match.group(1)) or None
    return None


def is_proposed_value(value: str | None) -> bool:
    return value is not None and PROPOSED_VALUE_RE.match(value) is not None


def declares_proposed_marker(lines: list[str]) -> bool:
    for line in lines[:STATUS_SCAN_LINES]:
        match = STATUS_FIELD_RE.match(line.lstrip(MARKER_DECORATION))
        if match and is_proposed_value(match.group(1)):
            return True
    return False


def marked_proposed_text(text: str) -> bool:
    lines = text.splitlines()
    status = declared_status(lines)
    if status is not None:
        return is_proposed_value(status)
    return declares_proposed_marker(lines)


def marked_proposed(path: Path) -> bool:
    try:
        return marked_proposed_text(path.read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return False


def governance_state(repo_root: Path = REPO_ROOT) -> str:
    """Classify the repository's governance state, or fail the build.

    Doctrine 6.1.1: a project is either pre-doctrine or governed, never
    partially. This function refuses to let the packaging pretend otherwise.
    """
    governance_dir = repo_root / GOVERNANCE
    record = repo_root.joinpath(*ADOPTION_RECORD)
    proposed = repo_root.joinpath(*PROPOSED_ADOPTION_RECORD)

    if not governance_dir.is_dir():
        return PRE_ADOPTION

    if record.is_file() and proposed.is_file():
        raise GovernanceStateError(
            "build refused: both a signed adoption record "
            f"({'/'.join(ADOPTION_RECORD)}) and an unsigned draft "
            f"({'/'.join(PROPOSED_ADOPTION_RECORD)}) exist. That is a "
            "contradictory governance state; resolve it before packaging.")

    if not record.is_file():
        return PRE_ADOPTION

    if marked_proposed(record):
        raise GovernanceStateError(
            f"build refused: {'/'.join(ADOPTION_RECORD)} exists but is still "
            "marked PROPOSED. An adoption record is signed or it is not.")

    still_proposed = sorted(
        p.relative_to(repo_root).as_posix()
        for p in governance_dir.rglob("*.md")
        if p.is_file() and marked_proposed(p))
    if still_proposed:
        raise GovernanceStateError(
            "build refused: the adoption record is signed but these governance "
            "documents are still marked PROPOSED, which is a partially adopted "
            "state: " + ", ".join(still_proposed))

    return ADOPTED


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_document_control(doctrine: Path) -> dict:
    """Extract DC.1 revision and status, and the DC.2 row for that revision."""
    revision = None
    status = None
    dc2_ratified = None

    lines = doctrine.read_text(encoding="utf-8").splitlines()
    for line in lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if "|" in line else []
        if len(cells) == 2:
            if cells[0].lower() == "revision" and revision is None:
                revision = cells[1]
            elif cells[0].lower() == "status" and status is None:
                status = cells[1]

    if revision is not None:
        for line in lines:
            if "|" not in line:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 4 and cells[0] == revision:
                dc2_ratified = cells[-1]
                break

    if revision is None or status is None:
        raise SystemExit("build: cannot read DC.1 revision and status from DOCTRINE.md")
    return {"revision": revision, "status": status, "dc2_ratified": dc2_ratified}


def is_ratified(control: dict) -> bool:
    status_ok = control["status"].strip().lower() == "ratified"
    dc2 = (control["dc2_ratified"] or "").strip().lower()
    dc2_ok = dc2 in ("yes", "ratified")
    return status_ok and dc2_ok


def archive_name(control: dict) -> str:
    revision = control["revision"]
    if is_ratified(control):
        return f"plumbline-{revision}.zip"
    return f"plumbline-{revision}-rc.zip"


def should_skip(path: Path, state: str = PRE_ADOPTION) -> bool:
    relative = path.relative_to(REPO_ROOT)
    if any(part in EXCLUDED_DIR_NAMES for part in relative.parts):
        return True
    if path.name in EXCLUDED_FILE_NAMES:
        return True
    if path.name.startswith(EXCLUDED_FILE_PREFIXES):
        return True
    if path.suffix.lower() in EXCLUDED_SUFFIXES:
        return True
    if path.name in NEVER_PACKAGED_NAMES:
        return True
    if relative.parts and relative.parts[0] == GOVERNANCE and state != ADOPTED:
        return True
    if relative.parts and relative.parts[0] == CLAUDE_DIR:
        if state != ADOPTED:
            return True
        return relative.as_posix() not in PACKAGED_CLAUDE_FILES
    return False


def collect_files(state: str = PRE_ADOPTION) -> list[Path]:
    files = [p for p in REPO_ROOT.rglob("*")
             if p.is_file() and not should_skip(p, state)]
    return sorted(files, key=lambda p: p.relative_to(REPO_ROOT).as_posix())


CRLF_CHECK_SUFFIXES = (".md", ".py", ".sh", ".json", ".txt", ".yml", ".yaml", ".toml")


class LineEndingError(SystemExit):
    """Raised to fail the build on CRLF in a packageable text artifact."""


def crlf_preflight(files: list[Path]) -> None:
    """Refuse to build while any packageable text artifact contains CRLF.

    Deliberately does NOT normalize. Silent normalization at packaging time
    produces an archive whose bytes differ from the working tree the release
    hash is supposed to describe. Fail loudly with the exact paths instead, so
    the tree is corrected before a hash exists.
    """
    offenders = sorted(
        path.relative_to(REPO_ROOT).as_posix()
        for path in files
        if path.suffix.lower() in CRLF_CHECK_SUFFIXES and b"\r\n" in path.read_bytes())
    if offenders:
        raise LineEndingError(
            "build refused: CRLF found in packageable text artifacts. "
            "Convert these to LF and rebuild; packaging will not normalize "
            "them silently.\n  " + "\n  ".join(offenders))


# --------------------------------------------------------------------------
# Machine-specific data preflight (RFI-15)
#
# Charter kill list: no release archive contains local absolute paths or
# machine-specific data. The checker enforces this against a built archive;
# this preflight refuses to produce the candidate in the first place, so a
# hash never exists for an archive that leaks the build host.
#
# "Machine-specific" means THIS machine's repository root or user home, in
# both separator spellings. It is deliberately NOT a generic "looks like an
# absolute path" scanner: documentation examples, regex sources, synthetic
# fixture strings, and historical evidence naming some OTHER machine are not
# machine-specific data and must never be rewritten to satisfy a gate.
#
# No packageable subtree is exempt for being historical. `archive/**` ships by
# the Owner's RFI-09 disposition, so it is checked exactly like every other
# packageable subtree.
# --------------------------------------------------------------------------

MACHINE_PATH_SUFFIXES = (".md", ".py", ".sh", ".json", ".txt", ".yml", ".yaml", ".toml")


class MachinePathError(SystemExit):
    """Raised to fail the build on machine-specific data in a shipped file."""


def machine_path_needles(repo_root: Path = REPO_ROOT) -> set[str]:
    """This build machine's own root and home, both separator spellings."""
    home = Path.home()
    needles = {str(repo_root), repo_root.as_posix(), str(home), home.as_posix()}
    return {needle for needle in needles if len(needle) > 3}


def machine_path_occurs(text: str, needle: str) -> bool:
    """True when an absolute host path occurs at textual path boundaries."""
    escaped = re.escape(needle)
    before = r"(?<![A-Za-z0-9_.-])"
    after = r"(?=$|[\\/\s\"'`\)\]\}>:;,.!?])"
    return re.search(before + escaped + after, text, re.IGNORECASE) is not None


def machine_path_preflight(files: list[Path], repo_root: Path = REPO_ROOT) -> None:
    """Refuse to build while a packageable text artifact names this machine."""
    needles = sorted(machine_path_needles(repo_root))
    offenders = []
    for path in files:
        if path.suffix.lower() not in MACHINE_PATH_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in needles:
            if machine_path_occurs(text, needle):
                offenders.append(
                    f"{path.relative_to(repo_root).as_posix()}  ({needle})")
                break
    if offenders:
        raise MachinePathError(
            "build refused: packageable text artifacts carry this build "
            "machine's own path. Redact them and rebuild; the charter kill "
            "list forbids machine-specific data in a release archive.\n  "
            + "\n  ".join(sorted(offenders)))


# --------------------------------------------------------------------------
# Deterministic ZIP policy (WO-PL-005-R1, RFI-11)
#
# The archive's bytes must be a function of file CONTENT and PATH only.
# Nothing about the build host may leak in.
#
# The two stdlib conveniences both leak host state and cannot be used here:
# ZipFile.write() inherits each file's mtime, the platform's creator-system
# code, and its on-disk permission bits; ZipFile.writestr() with a plain name
# stamps the current time. Either one makes the published SHA-256 impossible
# to reproduce from a fresh checkout, whose mtimes are always different.
#
# So every entry, MANIFEST.sha256 included, is written through an explicit
# ZipInfo with these fixed:
#
#   timestamp     the earliest instant the ZIP format can represent. The value
#                 is arbitrary; that it is a CONSTANT is the point
#   create_system 3 (Unix), so external_attr carries a meaningful mode instead
#                 of varying with the building OS
#   permissions   0755 for shell scripts an adopter is meant to execute, 0644
#                 for every other regular file. Never inherited: Windows and
#                 POSIX checkouts disagree about what is on disk
#   compression   ZIP_STORED. Deflate output is not guaranteed byte-identical
#                 across zlib builds and this repository has no evidence that
#                 it is. The package is small; reproducibility is worth more
#                 than the compression ratio
#   extra/comment empty per entry, and an empty archive comment
#   order         sorted by archive path, with the manifest sorted in place
#                 rather than appended last
#
# Source bytes are never normalized here. CRLF is refused by crlf_preflight()
# before a single byte is written, rather than silently rewritten.
# --------------------------------------------------------------------------

ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ZIP_CREATE_SYSTEM = 3
ZIP_COMPRESSION = zipfile.ZIP_STORED
ZIP_VERSION = 20
MODE_EXECUTABLE = 0o755
MODE_REGULAR = 0o644
S_IFREG = 0o100000
EXECUTABLE_SUFFIXES = (".sh",)


def is_executable_artifact(relative: str) -> bool:
    """True for files distributed so an adopter can execute them directly."""
    return relative.endswith(EXECUTABLE_SUFFIXES)


def zip_entry(arcname: str, executable: bool) -> zipfile.ZipInfo:
    """A fully specified entry header. Nothing is inherited from the host."""
    info = zipfile.ZipInfo(filename=arcname, date_time=ZIP_TIMESTAMP)
    info.compress_type = ZIP_COMPRESSION
    info.create_system = ZIP_CREATE_SYSTEM
    info.create_version = ZIP_VERSION
    info.extract_version = ZIP_VERSION
    mode = MODE_EXECUTABLE if executable else MODE_REGULAR
    info.external_attr = (S_IFREG | mode) << 16
    info.internal_attr = 0
    info.extra = b""
    info.comment = b""
    return info


def build(output_dir: Path) -> tuple[Path, str, int]:
    control = read_document_control(REPO_ROOT / "DOCTRINE.md")
    name = archive_name(control)
    state = governance_state()
    transient_release_preflight()

    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / name
    if target.exists():
        target.unlink()

    files = collect_files(state)
    crlf_preflight(files)
    machine_path_preflight(files)
    manifest_lines = []
    for path in files:
        relative = path.relative_to(REPO_ROOT).as_posix()
        manifest_lines.append(f"{sha256_file(path)}  {relative}")
    manifest = "\n".join(manifest_lines) + "\n"

    entries = []
    for path in files:
        relative = path.relative_to(REPO_ROOT).as_posix()
        entries.append((f"{ARCHIVE_ROOT}/{relative}",
                        path.read_bytes(),
                        is_executable_artifact(relative)))
    entries.append((f"{ARCHIVE_ROOT}/{MANIFEST_NAME}",
                    manifest.encode("utf-8"),
                    False))
    entries.sort(key=lambda entry: entry[0])

    with zipfile.ZipFile(target, "w", compression=ZIP_COMPRESSION) as archive:
        archive.comment = b""
        for arcname, data, executable in entries:
            archive.writestr(zip_entry(arcname, executable), data)

    return target, control["revision"], len(files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Plumbline distribution archive.")
    parser.add_argument("--output", default="dist/", help="output directory (default: dist/)")
    args = parser.parse_args(argv)

    output_dir = Path(args.output)
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir

    control = read_document_control(REPO_ROOT / "DOCTRINE.md")
    target, revision, count = build(output_dir)
    digest = sha256_file(target)

    state = "RATIFIED" if is_ratified(control) else "CANDIDATE (not ratified)"
    gov = governance_state()
    print(f"doctrine revision : {revision}")
    print(f"DC.1 status       : {control['status']}")
    print(f"DC.2 ratified     : {control['dc2_ratified']}")
    print(f"release state     : {state}")
    print(f"governance state  : {gov}"
          + ("  (governance/ excluded from the archive)" if gov == PRE_ADOPTION
             else "  (finalized governance/ instance included)"))
    # An --output outside the repository has no repository-relative
    # spelling; reporting it must not fail a build that already
    # collected, gated, wrote and hashed a valid archive.
    location = (target.relative_to(REPO_ROOT).as_posix()
                if target.is_relative_to(REPO_ROOT) else target.as_posix())
    print(f"archive           : {location}")
    print(f"files             : {count} (plus {MANIFEST_NAME})")
    print(f"sha256            : {digest}")
    print()
    print("This is a SOURCE DISTRIBUTION, not an overlay. Do not unpack it into "
          "an adopting project; instantiate the project-side artifacts through "
          "the routes in ADOPTING.md.")
    if not is_ratified(control):
        print()
        print("This is a candidate archive. It is not a release. A final "
              "non-candidate name is refused until DC.1 and DC.2 both record "
              "ratification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
