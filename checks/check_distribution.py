#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Deterministic distribution checks for the Plumbline methodology repository.

Standard library only. Exits nonzero on the first category of failure found,
after reporting every failure it found. These are mechanical checks over the
repository's own consistency, not judgment: nothing here decides anything the
Owner must decide.

Usage:
    python checks/check_distribution.py
    python checks/check_distribution.py --archive dist/plumbline-0.6-rc.zip
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import stat
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCTRINE = REPO_ROOT / "DOCTRINE.md"
BUILDER = REPO_ROOT / "scripts" / "build_distribution.py"
ADAPTER = REPO_ROOT / "adapters" / "claude-code" / "wo_capability_wall.py"


def machine_path_occurs(text: str, needle: str) -> bool:
    """Mirror the builder's absolute-path boundary rule for archive checks."""
    escaped = re.escape(needle)
    before = r"(?<![A-Za-z0-9_.-])"
    after = r"(?=$|[\\/\s\"'`\)\]\}>:;,.!?])"
    return re.search(before + escaped + after, text, re.IGNORECASE) is not None
ADAPTER_README = REPO_ROOT / "adapters" / "claude-code" / "README.md"
RATIFICATION_DRAFT = REPO_ROOT / "decisions" / "RATIFICATION-RECORD-DRAFT.md"
NO_AUTHORITY_MARKER = "DRAFT — NO AUTHORITY"

DECISIONS_DIR = REPO_ROOT / "decisions"
LICENSING_DIRECTION = REPO_ROOT / "decisions" / "LICENSING-DIRECTION.md"
LICENSE_CHECKER = REPO_ROOT / "checks" / "check_licenses.py"
PROJECTION_RECORDS = (
    "PROJECTION-MANIFEST.sha256",
    "PROJECTION-PROVENANCE.md",
    "projection/public-files.txt",
)
PROJECTION_DENIED_PREFIXES = ("archive/", "dist/", "governance/history/")

# WO-PL-022 B.3 item 6: executable documentation-truth rule. A public claim of
# an evidence-backed pilot must fail deterministically when the evidence it
# points to is absent from the tree.
PILOT_EXAMPLE = REPO_ROOT / "examples" / "plumbline-self-hosting-pilot.md"

# The v0.1 determination (DR-001, 2026-08-16): proposed only, never ratified.
ARCHIVE_V01 = REPO_ROOT / "archive" / "proposed-v0.1"
ARCHIVED_PROPOSAL = ARCHIVE_V01 / "decisions" / "DR-001-PROPOSAL-NEVER-RATIFIED.md"
PROPOSAL_MARKER = "PROPOSAL — NEVER RATIFIED — NO AUTHORITY"
ORIGINAL_BLOB_SHA = "9cf9aa5f188a5351d4c12b53763b4c3c4688ba28efefb57a284a2fcf120e74ab"
BASELINE_COMMIT = "6e165e585f907baf83a787ba5cc71270a5a4652e"

# Documents that describe the current state. Historical work orders and
# remediation reports are deliberately excluded: they record what was true when
# written and are never edited to describe a later state.
CURRENT_DOCUMENTS = (
    "README.md",
    "REUSE.toml",
    "LICENSE-MAP.md",
    "NAMING.md",
    "PUBLICATION.md",
    "CONTRIBUTING.md",
    "ADOPTING.md",
    "SELF-HOSTING.md",
    "SECURITY.md",
    "DOCTRINE.md",
    "decisions/README.md",
    "decisions/DR-001.md",
    "decisions/DR-003.md",
    "skills/plumbline-adopt/LICENSE-MAP.md",
)

# The candidate-phrase scan excludes the ratification record itself: a record of
# a transition has to be able to name the status it changed from. That the
# record asserts ratification is checked directly instead.
CANDIDATE_SCAN_DOCUMENTS = tuple(
    name for name in CURRENT_DOCUMENTS if name != "decisions/DR-001.md")

# Once ratified, no current document may still present 0.6 as a candidate.
CANDIDATE_CLAIM_PHRASES = (
    "ratification candidate",
    "not yet ratified",
    "is a candidate",
)

# v0.1 may never be presented as having carried authority.
V01_AUTHORITY_CLAIM_PHRASES = (
    "v0.1 was ratified",
    "0.1 is ratified",
    "ratified charter v0.1",
    "ratification of doctrine charter v0.1",
    "ratified revision 0.1",
)

SKILL = REPO_ROOT / "skills" / "plumbline-adopt"

TEMPLATE_FILES = {
    "A": "A-charter.md",
    "B": "B-work-order.md",
    "C": "C-owner-brief.md",
    "D": "D-adoption-record.md",
    "E": "E-adoption-mapping.md",
}

# Skill-bundle copy -> canonical source. The bundle must be self-contained,
# so every one of these is a byte-for-byte copy (Route B, ADOPTING.md 3).
DISPATCH_CHECKER = REPO_ROOT / "checks" / "check_work_order_dispatch.py"

BUNDLE_COPIES = {
    SKILL / "references" / "DOCTRINE.md": DOCTRINE,
    SKILL / "references" / "migration-guides" / "0.1-to-0.6.md":
        REPO_ROOT / "migration-guides" / "0.1-to-0.6.md",
    SKILL / "references" / "migration-guides" / "0.6-to-0.7.md":
        REPO_ROOT / "migration-guides" / "0.6-to-0.7.md",
    SKILL / "references" / "migration-guides" / "0.7-to-0.8.md":
        REPO_ROOT / "migration-guides" / "0.7-to-0.8.md",
    SKILL / "assets" / "adapters" / "claude-code" / "README.md": ADAPTER_README,
    SKILL / "assets" / "adapters" / "claude-code" / "wo_capability_wall.py": ADAPTER,
    SKILL / "assets" / "checks" / "check_work_order_dispatch.py": DISPATCH_CHECKER,
    **{
        SKILL / "assets" / "templates" / name: REPO_ROOT / "templates" / name
        for name in TEMPLATE_FILES.values()
    },
}

REQUIRED_FILES = [
    ".github/workflows/ci.yml",
    ".gitattributes",
    ".gitignore",
    "ADOPTING.md",
    "CLAUDE.md",
    "DOCTRINE.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "LICENSE-MAP.md",
    "LICENSES/Apache-2.0.txt",
    "LICENSES/CC-BY-4.0.txt",
    "LICENSES/CC0-1.0.txt",
    "LICENSES/MIT-0.txt",
    "NAMING.md",
    "PUBLICATION.md",
    "README.md",
    "SELF-HOSTING.md",
    "init.sh",
    "adapters/claude-code/README.md",
    "adapters/claude-code/wo_capability_wall.py",
    "archive/README.md",
    "checks/check_distribution.py",
    "checks/check_licenses.py",
    "checks/check_public_projection.py",
    "checks/check_work_order_dispatch.py",
    "decisions/DR-001.md",
    "decisions/DR-003.md",
    "decisions/DR-004.md",
    "decisions/DR-005.md",
    "decisions/LICENSING-DIRECTION.md",
    "decisions/README.md",
    "examples/README.md",
    "migration-guides/0.1-to-0.6.md",
    "migration-guides/0.6-to-0.7.md",
    "migration-guides/0.7-to-0.8.md",
    "scripts/build_distribution.py",
    "scripts/build_public_projection.py",
    "skills/plumbline-adopt/SKILL.md",
    "skills/plumbline-adopt/LICENSE-MAP.md",
    "tests/test_init_sh.py",
    "tests/test_distribution.py",
    "tests/test_check_licenses.py",
    "tests/test_wo_capability_wall.py",
    "tests/test_check_work_order_dispatch.py",
    "tests/test_public_projection.py",
    "projection/public-files.txt",
    *[f"templates/{name}" for name in TEMPLATE_FILES.values()],
    *[str(p.relative_to(REPO_ROOT)).replace("\\", "/") for p in BUNDLE_COPIES],
]

# Paths that must never appear outside the historical archive.
FORBIDDEN_DIR_NAMES = frozenset({"mnt", "user-data"})
FORBIDDEN_NAME_PATTERNS = (
    re.compile(r"^DOCTRINE_v[\d.]+\.md$"),
    re.compile(r"^wo_capability_wall_v\d+\.py$"),
    re.compile(r"^REMEDIATION_COMPANION.*$"),
)
SCAN_EXCLUDED_DIRS = frozenset({".git", "dist", "archive", "__pycache__", ".pytest_cache"})

# Literal claims that may not appear while the revision is a candidate.
# Derived from the document's own current revision rather than hard-coded, so
# this scan stays correct as DOCTRINE.md's DC.1 revision advances.
def ratified_claim_phrases(revision: str) -> tuple[str, ...]:
    return (
        f"ratified revision {revision}",
        f"authoritative revision {revision}",
        f"revision {revision} is ratified",
        f"{revision} is authoritative",
    )

# Doctrine 5.1.5: Plumbline's own working records are never carried into an
# adopting project. The adoption skill bundle is the one route that copies a
# directory wholesale, so it is the one that must be policed mechanically.
SELF_HOSTED_RECORD_NAMES = frozenset({
    "CLAUDE.md",
    "SELF-HOSTING.md",
    "PLAN.md",
    "STATE.md",
    "ROUTING.md",
    "LOG.md",
    "RATIFICATION-RECORD-DRAFT.md",
    "DR-001.md",
    "LICENSING-DIRECTION.md",
})
SELF_HOSTED_RECORD_DIRS = frozenset({"governance", "decisions", "bootstrap", "archive"})

# The canonical short description (WO-PL-002 item 5.1), required verbatim.
CANONICAL_DESCRIPTION = (
    "Plumbline is a document-controlled governance methodology with a "
    "self-hosting reference implementation and project-scaffolding toolkit."
)

# The source-distribution distinction (WO-PL-002 item 5.2) must be stated
# where someone about to unpack the archive will look.
SOURCE_DISTRIBUTION_PHRASE = "source distribution, not an overlay"

# Governance packaging gate (Owner disposition, 2026-08-16). Mirrors
# scripts/build_distribution.py; the two must agree or the check is theatre.
GOVERNANCE = "governance"
ADOPTION_RECORD = REPO_ROOT / "governance" / "decisions" / "DR-001.md"
PROPOSED_ADOPTION_RECORD = (
    REPO_ROOT / "governance" / "decisions" / "DR-001-ADOPTION-PROPOSED.md")
NEVER_PACKAGED_NAMES = frozenset({"DR-001-ADOPTION-PROPOSED.md"})
STATUS_SCAN_LINES = 40
FRONTMATTER_FENCES = ("---", "...")
MARKER_DECORATION = "#>*_` \t"
STATUS_FIELD_RE = re.compile(r"^status\s*:\s*(.*)$", re.IGNORECASE)
PROPOSED_VALUE_RE = re.compile(r"^[\s'\"`*_]*proposed\b", re.IGNORECASE)
PRE_ADOPTION = "pre-adoption"
ADOPTED = "adopted"

# Provider installation. Registered hooks must be portable: Claude Code
# supplies ${CLAUDE_PROJECT_DIR}, and an absolute path bakes one machine's
# layout into a governed artifact.
CLAUDE_DIR = REPO_ROOT / ".claude"
SETTINGS = CLAUDE_DIR / "settings.json"
INSTALLED_ADAPTER = CLAUDE_DIR / "hooks" / "wo_capability_wall.py"
PROJECT_DIR_VAR = "${CLAUDE_PROJECT_DIR}"

# Post-adoption, the archive carries exactly these two installation files.
PACKAGED_CLAUDE_FILES = frozenset({
    ".claude/settings.json",
    ".claude/hooks/wo_capability_wall.py",
})
NEVER_PACKAGED_CLAUDE = (
    ".claude/settings.local.json",
    ".claude/active-wo.txt",
)

# Text artifacts must be LF in the working tree before a release hash exists.
CRLF_CHECK_SUFFIXES = (".md", ".py", ".sh", ".json", ".txt", ".yml", ".yaml", ".toml")


class Failures:
    def __init__(self):
        self.items: list[str] = []

    def add(self, category: str, detail: str) -> None:
        self.items.append(f"[{category}] {detail}")

    def __bool__(self) -> bool:
        return bool(self.items)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# Document control
# --------------------------------------------------------------------------

def document_control() -> dict:
    revision = status = dc2 = None
    lines = read_text(DOCTRINE).splitlines()
    for line in lines:
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2:
            if cells[0].lower() == "revision" and revision is None:
                revision = cells[1]
            elif cells[0].lower() == "status" and status is None:
                status = cells[1]
    if revision:
        for line in lines:
            if "|" not in line:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 4 and cells[0] == revision:
                dc2 = cells[-1]
                break
    return {"revision": revision, "status": status, "dc2_ratified": dc2}


def resolve_ratification_record(revision: str, failures: Failures) -> Path | None:
    """The decisions/DR-*.md record that names `revision` as ratified.

    Fail-closed: DR-001 is not privileged. Every ratified revision names its
    own ratification record in its own `| Revision ratified | x.y |` row, so
    the record is resolved from that row rather than a hard-coded filename.
    If none or more than one decisions/DR-*.md record names this revision,
    no record is returned and a failure is recorded rather than guessing.
    """
    if not DECISIONS_DIR.is_dir():
        failures.add("markers", f"{rel(DECISIONS_DIR)} does not exist")
        return None
    candidates = []
    for path in sorted(DECISIONS_DIR.glob("DR-*.md")):
        for line in read_text(path).splitlines():
            if "|" not in line:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if (len(cells) == 2 and cells[0].lower() == "revision ratified"
                    and cells[1] == revision):
                candidates.append(path)
                break
    if len(candidates) != 1:
        failures.add(
            "markers",
            f"expected exactly one decisions/DR-*.md record with "
            f"'Revision ratified | {revision}', found {len(candidates)}")
        return None
    return candidates[0]


def check_markers(control: dict, failures: Failures) -> None:
    revision, status, dc2 = control["revision"], control["status"], control["dc2_ratified"]
    if not revision or not status:
        failures.add("markers", "DOCTRINE.md DC.1 revision or status is unreadable")
        return
    if dc2 is None:
        failures.add("markers", f"DOCTRINE.md DC.2 has no row for revision {revision}")
        return

    status_ratified = status.strip().lower() == "ratified"
    dc2_ratified = dc2.strip().lower() in ("yes", "ratified")

    if status_ratified != dc2_ratified:
        failures.add(
            "markers",
            f"DC.1 Status is {status!r} but the DC.2 row for {revision} says {dc2!r}; "
            "the candidate and ratified markers contradict each other")

    if not status_ratified:
        if RATIFICATION_DRAFT.is_file():
            text = read_text(RATIFICATION_DRAFT)
            if NO_AUTHORITY_MARKER not in text:
                failures.add(
                    "markers",
                    f"{RATIFICATION_DRAFT.name} lacks its {NO_AUTHORITY_MARKER!r} marker")
        else:
            failures.add(
                "markers",
                f"revision {revision} is a candidate but {RATIFICATION_DRAFT.name} is absent")

        phrases = ratified_claim_phrases(revision)
        for path in scan_paths():
            if path.suffix.lower() != ".md":
                continue
            lowered = read_text(path).lower()
            for phrase in phrases:
                if phrase in lowered:
                    failures.add(
                        "markers",
                        f"{rel(path)} claims {phrase!r} while DC.1 records a candidate")
    else:
        if RATIFICATION_DRAFT.is_file() and NO_AUTHORITY_MARKER in read_text(RATIFICATION_DRAFT):
            failures.add(
                "markers",
                f"DC.1 records {revision} as ratified but an unsigned "
                f"{RATIFICATION_DRAFT.name} is still present")

        ratification_record = resolve_ratification_record(revision, failures)
        if ratification_record is not None:
            record = read_text(ratification_record)
            if NO_AUTHORITY_MARKER in record:
                failures.add("markers",
                             f"{rel(ratification_record)} still carries the draft "
                             "no-authority marker")

        # The footer must agree with DC.1.
        footer = [l.strip() for l in read_text(DOCTRINE).splitlines()
                  if re.match(r"^\*Revision .*\*$", l.strip())]
        if not footer:
            failures.add("markers", "DOCTRINE.md has no revision footer")
        for line in footer:
            if "candidate" in line.lower():
                failures.add("markers",
                             f"DOCTRINE.md footer still calls {revision} a candidate "
                             "while DC.1 records it as ratified")
            if "ratified" not in line.lower():
                failures.add("markers",
                             "DOCTRINE.md footer does not record ratification")

        # No current document may still present the revision as a candidate.
        for name in CANDIDATE_SCAN_DOCUMENTS:
            path = REPO_ROOT / name
            if not path.is_file():
                continue
            lowered = read_text(path).lower()
            for phrase in CANDIDATE_CLAIM_PHRASES:
                if phrase in lowered:
                    failures.add(
                        "markers",
                        f"{name} still describes the revision with {phrase!r} while "
                        "DC.1 records it as ratified")


def check_v01_determination(failures: Failures) -> None:
    """DR-001: v0.1 was proposed only and never ratified."""
    lines = read_text(DOCTRINE).splitlines()

    row = None
    for line in lines:
        if line.startswith("| 0.1 |"):
            row = [c.strip() for c in line.strip().strip("|").split("|")]
            break
    if row is None:
        failures.add("v0.1", "DOCTRINE.md DC.2 has no row for revision 0.1")
    elif row[-1].strip().lower() not in ("no", "never"):
        failures.add("v0.1",
                     f"DC.2's 0.1 row records ratified={row[-1]!r}; v0.1 was never ratified")

    if (REPO_ROOT / "archive" / "unresolved-v0.1").exists():
        failures.add("v0.1", "archive/unresolved-v0.1/ still exists; it was renamed "
                             "to archive/proposed-v0.1/ when the question was resolved")
    if not ARCHIVE_V01.is_dir():
        failures.add("v0.1", f"{rel(ARCHIVE_V01)} does not exist")
    if not ARCHIVED_PROPOSAL.is_file():
        failures.add("v0.1", f"{rel(ARCHIVED_PROPOSAL)} does not exist")
    else:
        text = read_text(ARCHIVED_PROPOSAL)
        if PROPOSAL_MARKER not in text:
            failures.add("v0.1",
                         f"{rel(ARCHIVED_PROPOSAL)} lacks the {PROPOSAL_MARKER!r} marker")
        # The active metadata form, not a quoted mention of it. The correction
        # notice inside the file has to be able to quote what it corrected.
        if re.search(r"^\s*\*\*Ratified by:", text, re.MULTILINE):
            failures.add("v0.1",
                         f"{rel(ARCHIVED_PROPOSAL)} still carries the inaccurate "
                         "'Ratified by:' metadata field")
        if not re.search(r"^\s*\*\*Proposed by:\*\*\s*HLLMR", text, re.MULTILINE):
            failures.add("v0.1",
                         f"{rel(ARCHIVED_PROPOSAL)} does not record 'Proposed by: HLLMR'")
        if "2026-08-14" not in text:
            failures.add("v0.1",
                         f"{rel(ARCHIVED_PROPOSAL)} does not record the 2026-08-14 "
                         "proposal date")

    # No stale directory name, and no claim that v0.1 held authority, in current docs.
    for name in CURRENT_DOCUMENTS:
        path = REPO_ROOT / name
        if not path.is_file():
            continue
        text = read_text(path)
        if "unresolved-v0.1" in text:
            failures.add("v0.1", f"{name} refers to the old archive path unresolved-v0.1")
        lowered = text.lower()
        for phrase in V01_AUTHORITY_CLAIM_PHRASES:
            if phrase in lowered:
                failures.add("v0.1", f"{name} claims {phrase!r}")


def check_archive_provenance(failures: Failures) -> None:
    """The Owner's correction of the archived proposal must stay auditable."""
    readme = REPO_ROOT / "archive" / "README.md"
    if not readme.is_file():
        failures.add("provenance", "archive/README.md does not exist")
        return
    text = read_text(readme)
    required = {
        "the original path": "decisions/DR-001.md",
        "the baseline commit": BASELINE_COMMIT,
        "the original blob hash": ORIGINAL_BLOB_SHA,
        "recoverability from Git history": "recoverable from Git history",
        "the correction date": "2026-08-16",
    }
    for label, needle in required.items():
        if needle not in text:
            failures.add("provenance", f"archive/README.md does not record {label}")
    # It must not claim the corrected copy is still byte-for-byte.
    if re.search(r"byte-for-byte", text) and "No byte-for-byte claim" not in text:
        failures.add("provenance",
                     "archive/README.md mentions byte-for-byte without disclaiming it "
                     "for the corrected file")


# --------------------------------------------------------------------------
# Required files and skill bundle
# --------------------------------------------------------------------------

def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def check_required_files(failures: Failures, *, projection: bool = False) -> None:
    required = set(REQUIRED_FILES)
    if projection:
        required.discard("archive/README.md")
        required.update(PROJECTION_RECORDS)
    for name in sorted(required):
        if not (REPO_ROOT / name).is_file():
            failures.add("required-file", f"missing: {name}")


def parse_projection_allowlist(raw: bytes, failures: Failures,
                               context: str) -> list[str]:
    try:
        entries = [line.strip() for line in raw.decode("utf-8").splitlines()
                   if line.strip()]
    except UnicodeDecodeError:
        failures.add("projection", f"{context} allowlist is not UTF-8")
        return []
    if entries != sorted(entries) or len(entries) != len(set(entries)):
        failures.add("projection",
                     f"{context} allowlist is not sorted and duplicate-free")
    for entry in entries:
        path = Path(entry)
        if (path.is_absolute() or "\\" in entry or
                any(part in ("", ".", "..") for part in entry.split("/"))):
            failures.add("projection", f"{context} allowlist has an unsafe path")
    return entries


def validate_projection_records(read_bytes, available: set[str],
                                failures: Failures, context: str) -> None:
    for relative in PROJECTION_RECORDS:
        if relative not in available:
            failures.add("projection", f"{context} missing: {relative}")
    if any(relative not in available for relative in PROJECTION_RECORDS):
        return
    try:
        allowlist_raw = read_bytes("projection/public-files.txt")
        manifest_raw = read_bytes("PROJECTION-MANIFEST.sha256")
        provenance_raw = read_bytes("PROJECTION-PROVENANCE.md")
    except (OSError, KeyError, zipfile.BadZipFile):
        failures.add("projection", f"{context} projection records are unreadable")
        return
    entries = parse_projection_allowlist(allowlist_raw, failures, context)
    try:
        lines = manifest_raw.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        failures.add("projection", f"{context} projection manifest is not UTF-8")
        return
    found: dict[str, str] = {}
    ordered: list[str] = []
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            failures.add("projection", f"{context} projection manifest is malformed")
            continue
        digest, relative = match.groups()
        if relative in found:
            failures.add("projection",
                         f"{context} projection manifest has a duplicate path")
        found[relative] = digest
        ordered.append(relative)
    if ordered != sorted(ordered):
        failures.add("projection",
                     f"{context} projection manifest is not path-sorted")
    expected = sorted([*entries, "PROJECTION-PROVENANCE.md"])
    if sorted(found) != expected:
        failures.add("projection",
                     f"{context} projection manifest coverage is incomplete")
    for relative, digest in found.items():
        if relative not in available:
            failures.add("projection",
                         f"{context} projection manifest names a missing payload")
            continue
        try:
            actual = hashlib.sha256(read_bytes(relative)).hexdigest()
        except (OSError, KeyError):
            failures.add("projection",
                         f"{context} projection payload is unreadable")
            continue
        if actual != digest:
            failures.add("projection",
                         f"{context} projection manifest digest mismatch")
    try:
        provenance = provenance_raw.decode("utf-8")
    except UnicodeDecodeError:
        failures.add("projection", f"{context} projection provenance is not UTF-8")
        return
    allow_digest = hashlib.sha256(allowlist_raw).hexdigest()
    required_patterns = (
        r"This candidate is derived from a private governed source repository\.",
        r"Legacy commit identifiers in projected records refer to that private",
        r"- Source commit: `(?:UNAVAILABLE|[0-9a-f]{40})`",
        r"- Source commit time: `[^`]+`",
        rf"- Projection allowlist SHA-256: `{allow_digest}`",
        r"^## Legacy identifier inventory$",
    )
    for pattern in required_patterns:
        if re.search(pattern, provenance, re.MULTILINE) is None:
            failures.add("projection",
                         f"{context} projection provenance is incomplete")
            break
    if "Private-pattern input SHA-256" in provenance:
        failures.add(
            "projection",
            f"{context} projection provenance discloses a private-pattern "
            "fingerprint")


def check_projection_records(failures: Failures) -> None:
    available = {
        path.relative_to(REPO_ROOT).as_posix()
        for path in REPO_ROOT.rglob("*") if path.is_file()
    }
    validate_projection_records(
        lambda relative: (REPO_ROOT / relative).read_bytes(),
        available, failures, "source")
    for relative in available:
        if any(relative == prefix[:-1] or relative.startswith(prefix)
               for prefix in PROJECTION_DENIED_PREFIXES):
            failures.add("projection",
                         f"source projection contains a private-only path: {relative}")


def check_license_records(failures: Failures) -> None:
    root_license = REPO_ROOT / "LICENSE"
    cc_by_code = REPO_ROOT / "LICENSES" / "CC-BY-4.0.txt"
    if root_license.is_file() and cc_by_code.is_file():
        if root_license.read_bytes() != cc_by_code.read_bytes():
            failures.add("license",
                         "LICENSE differs from LICENSES/CC-BY-4.0.txt")
    if LICENSING_DIRECTION.is_file():
        direction = read_text(LICENSING_DIRECTION)
        if "SUPERSEDED" not in direction or "decisions/DR-003.md" not in direction:
            failures.add(
                "license",
                "decisions/LICENSING-DIRECTION.md lacks the DR-003 "
                "supersession marker")


def check_license_mechanization(failures: Failures) -> None:
    if not LICENSE_CHECKER.is_file():
        return
    spec = importlib.util.spec_from_file_location(
        "_plumbline_check_licenses", LICENSE_CHECKER
    )
    if spec is None or spec.loader is None:
        failures.add("license-gate", "cannot load checks/check_licenses.py")
        return
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        findings = module.check(REPO_ROOT, include_untracked=True)
    except Exception as exc:  # fail closed at the public gate boundary
        failures.add("license-gate", f"checker failed to run: {exc}")
        return
    for finding in findings:
        failures.add("license-gate", finding)


def check_bundle_copies(failures: Failures) -> None:
    for copy, source in sorted(BUNDLE_COPIES.items()):
        if not source.is_file():
            failures.add("bundle", f"canonical source missing: {rel(source)}")
            continue
        if not copy.is_file():
            failures.add("bundle", f"bundle copy missing: {rel(copy)}")
            continue
        copy_bytes, source_bytes = copy.read_bytes(), source.read_bytes()
        if copy_bytes == source_bytes:
            continue
        if copy_bytes.splitlines() == source_bytes.splitlines():
            failures.add(
                "bundle",
                f"{rel(copy)} differs from {rel(source)} in line endings only")
        else:
            failures.add(
                "bundle", f"{rel(copy)} differs in content from {rel(source)}")


def check_self_hosting_segregation(failures: Failures) -> None:
    """Doctrine 5.1.5: no Plumbline working record reaches an adopting project.

    The skill bundle is copied wholesale into a target repository, so anything
    inside it is, by construction, something an adopter receives.
    """
    if not SKILL.is_dir():
        failures.add("segregation", "the adoption skill bundle is missing")
        return

    allowed = {SKILL / "SKILL.md", SKILL / "LICENSE-MAP.md",
               *BUNDLE_COPIES.keys()}
    for path in sorted(SKILL.rglob("*")):
        if not path.is_file():
            continue
        if path.name in SELF_HOSTED_RECORD_NAMES:
            failures.add(
                "segregation",
                f"{rel(path)} carries a Plumbline working record into the "
                "adoption bundle (Doctrine 5.1.5)")
        relative_parts = path.relative_to(SKILL).parts[:-1]
        for part in relative_parts:
            if part in SELF_HOSTED_RECORD_DIRS:
                failures.add(
                    "segregation",
                    f"{rel(path)} lies under a '{part}' directory inside the "
                    "adoption bundle (Doctrine 5.1.5)")
        if path not in allowed:
            failures.add(
                "segregation",
                f"{rel(path)} is an unrecognized file in the adoption bundle; "
                "the bundle carries only SKILL.md and the declared copies")

    # The scaffolder must copy templates and the adapter, and nothing else.
    init_text = read_text(REPO_ROOT / "init.sh") if (REPO_ROOT / "init.sh").is_file() else ""
    for name in ("CLAUDE.md", "SELF-HOSTING.md", "DOCTRINE.md"):
        if f'cp "$HERE/{name}"' in init_text or f"cp $HERE/{name}" in init_text:
            failures.add("segregation", f"init.sh copies {name} into the target project")


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
# This block is mirrored verbatim in scripts/build_distribution.py. The
# builder and the checker must agree on every document or the gate is theatre.
# --------------------------------------------------------------------------

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


def marked_proposed(text: str) -> bool:
    lines = text.splitlines()
    status = declared_status(lines)
    if status is not None:
        return is_proposed_value(status)
    return declares_proposed_marker(lines)


def governance_state(failures: Failures | None = None) -> str:
    """Classify the governance state; record a failure on a contradiction."""
    governance_dir = REPO_ROOT / GOVERNANCE
    if not governance_dir.is_dir():
        return PRE_ADOPTION

    if ADOPTION_RECORD.is_file() and PROPOSED_ADOPTION_RECORD.is_file():
        if failures is not None:
            failures.add("governance-state",
                         "both a signed adoption record and an unsigned draft "
                         "exist; the governance state is contradictory")
        return PRE_ADOPTION
    if not ADOPTION_RECORD.is_file():
        return PRE_ADOPTION
    if marked_proposed(read_text(ADOPTION_RECORD)):
        if failures is not None:
            failures.add("governance-state",
                         f"{rel(ADOPTION_RECORD)} exists but is still marked PROPOSED")
        return PRE_ADOPTION

    still_proposed = sorted(
        rel(p) for p in governance_dir.rglob("*.md")
        if p.is_file() and marked_proposed(read_text(p)))
    if still_proposed:
        if failures is not None:
            failures.add("governance-state",
                         "the adoption record is signed but these remain "
                         "PROPOSED: " + ", ".join(still_proposed))
        return PRE_ADOPTION
    return ADOPTED


def check_governance_packaging(failures: Failures) -> None:
    """The gate itself, independent of any built archive."""
    state = governance_state(failures)
    if state == PRE_ADOPTION and PROPOSED_ADOPTION_RECORD.is_file():
        # Correct and expected before adoption; assert it is never packaged.
        pass
    for name in NEVER_PACKAGED_NAMES:
        for path in REPO_ROOT.rglob(name):
            if SKILL in path.parents:
                failures.add("governance-state",
                             f"{rel(path)} is inside the adoption bundle")


def check_hook_registration(failures: Failures) -> None:
    """The project hook registration must be portable and must match canon."""
    if not SETTINGS.is_file():
        return
    try:
        data = json.loads(read_text(SETTINGS))
    except ValueError as exc:
        failures.add("hook-registration", f".claude/settings.json is not valid JSON: {exc}")
        return

    entries = (data.get("hooks") or {}).get("PreToolUse") or []
    hooks = [h for entry in entries for h in (entry.get("hooks") or [])]
    commands = [h.get("command", "") for h in hooks]
    matchers = [entry.get("matcher") for entry in entries]

    if not commands:
        failures.add("hook-registration",
                     ".claude/settings.json declares no PreToolUse command")
        return
    if "*" not in matchers:
        failures.add("hook-registration",
                     f"PreToolUse matcher is {matchers!r}; the adapter requires '*' "
                     "so unknown tools are denied rather than unmatched")
    if len(entries) != 1 or len(hooks) != 1:
        failures.add(
            "hook-registration",
            "project settings must declare exactly one PreToolUse matcher and one command hook")

    for hook in hooks:
        timeout = hook.get("timeout")
        if (not isinstance(timeout, (int, float)) or isinstance(timeout, bool)
                or timeout <= 0):
            failures.add(
                "hook-registration",
                "PreToolUse command hook lacks an explicit positive timeout")
        if hook.get("type") != "command":
            failures.add("hook-registration", "PreToolUse hook type is not 'command'")

    for command in commands:
        if PROJECT_DIR_VAR not in command:
            failures.add(
                "hook-registration",
                f"hook command does not use {PROJECT_DIR_VAR}: {command!r}. "
                "A registration without it is not portable across clones")
        for absolute in (str(REPO_ROOT), REPO_ROOT.as_posix()):
            if absolute.lower() in command.lower():
                failures.add(
                    "hook-registration",
                    f"hook command contains an absolute repository path "
                    f"({absolute}); use {PROJECT_DIR_VAR}")
        if re.search(r'"[A-Za-z]:[\\/]', command) or re.search(r'"/(?:home|Users)/', command):
            failures.add("hook-registration",
                         f"hook command contains an absolute path: {command!r}")
        if not (command.strip().startswith("py -3 ")
                or command.strip().startswith("python3 ")):
            failures.add(
                "hook-registration",
                "hook command must use native Windows 'py -3' or native POSIX 'python3'")

    # The installed adapter must be the canonical one, byte for byte.
    if INSTALLED_ADAPTER.is_file() and ADAPTER.is_file():
        if INSTALLED_ADAPTER.read_bytes() != ADAPTER.read_bytes():
            failures.add(
                "hook-registration",
                f"{rel(INSTALLED_ADAPTER)} differs from the canonical "
                f"{rel(ADAPTER)}; the installed wall must be the shipped wall")


def crlf_offenders(root: Path, names: list[str] | None = None) -> list[str]:
    """Return packageable text artifacts containing CRLF."""
    offenders = []
    paths = ([root / n for n in names] if names is not None
             else [p for p in root.rglob("*") if p.is_file()])
    for path in paths:
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SCAN_EXCLUDED_DIRS or part == ".git" for part in relative.parts):
            continue
        if path.suffix.lower() not in CRLF_CHECK_SUFFIXES:
            continue
        if b"\r\n" in path.read_bytes():
            offenders.append(relative.as_posix())
    return sorted(offenders)


def check_line_endings(failures: Failures) -> None:
    """Deterministic CRLF preflight. Never normalizes; only reports."""
    for offender in crlf_offenders(REPO_ROOT):
        failures.add("line-endings",
                     f"{offender} contains CRLF. Convert it to LF before "
                     "building; packaging must not normalize silently, or the "
                     "release hash stops matching the working tree")


# --------------------------------------------------------------------------
# Source-mode machine-path parity (RFI-23)
#
# `scripts/build_distribution.py` refuses to package a source tree whose
# packageable text artifacts name this machine's own repository root or user
# home. The equivalent scan here lived only inside `check_archive()`, which
# runs only when `--archive` is supplied, so a source-mode run performed no
# machine-path scan at all.
#
# The two gates never disagreed about the RULE. They disagreed about WHEN it
# is applied: the builder to the source tree, the checker only to a built
# archive. "Source check passes" was therefore not equivalent to "source tree
# is buildable", and the defect surfaced later as a build refusal cascading
# across the test suite rather than as one legible check failure.
#
# The rule itself is NOT restated here. The packageable file set, the needle
# definition, and the scanned suffixes are all read from the builder, so there
# is exactly one definition of machine-specific data in the repository and a
# change to it cannot leave the two gates disagreeing again.
#
# Only the REPORTING differs, and it must: the builder raises on the first
# offending set because it is refusing to produce a candidate, while this
# checker aggregates every failure across every category before exiting. That
# is why this is a loop here rather than a direct call to the builder's
# `machine_path_preflight()`, which raises SystemExit and would abandon the
# remaining checks.
# --------------------------------------------------------------------------

def load_builder():
    spec = importlib.util.spec_from_file_location("_builder_check", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_transient_release_state(failures: Failures) -> None:
    """Aggregate every transient live-work path the builder would refuse.

    Consumes the builder's single `is_transient_release_path` /
    `transient_release_paths` definition rather than restating a second deny
    list here; see `scripts/build_distribution.py`'s WO-PL-015 block.
    """
    if not BUILDER.is_file():
        return
    try:
        builder = load_builder()
    except Exception as exc:  # noqa: BLE001 - a broken builder is a real failure
        failures.add("transient-release-state",
                     f"the builder will not import, so transient release "
                     f"state cannot be checked: {type(exc).__name__}: {exc}")
        return
    for relative in builder.transient_release_paths(REPO_ROOT):
        failures.add(
            "transient-release-state",
            f"{relative} is transient live-work state; a release candidate "
            "is a between-work-order checkpoint, never an in-progress "
            "implementation envelope")


def check_source_machine_paths(failures: Failures) -> None:
    """Fail the source tree on what the builder would refuse to package."""
    if not BUILDER.is_file():
        return
    try:
        builder = load_builder()
        # A checker scanning a different tree than the builder packages would
        # report parity it is not testing.
        if Path(builder.REPO_ROOT).resolve() != REPO_ROOT:
            failures.add("machine-path",
                         "the builder resolves a different repository root than "
                         "this checker; source-mode parity cannot be asserted")
            return
        files = builder.collect_files(governance_state())
        needles = sorted(builder.machine_path_needles(REPO_ROOT))
        suffixes = builder.MACHINE_PATH_SUFFIXES
    except Exception as exc:  # noqa: BLE001 - a broken builder is a real failure
        failures.add("machine-path",
                     f"the builder will not import, so the source tree cannot be "
                     f"scanned for machine-specific data: {type(exc).__name__}: {exc}")
        return

    for path in files:
        if path.suffix.lower() not in suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in needles:
            if builder.machine_path_occurs(text, needle):
                failures.add("machine-path",
                             f"{rel(path)} contains this machine's own path "
                             f"({needle}); the charter kill list forbids "
                             "machine-specific data in a release archive, and "
                             "the builder refuses to package this tree")
                break


def check_positioning(failures: Failures) -> None:
    """The canonical description and the source-distribution distinction."""
    readme = REPO_ROOT / "README.md"
    if not readme.is_file():
        return
    text = read_text(readme)
    collapsed = " ".join(text.split())
    if CANONICAL_DESCRIPTION not in collapsed:
        failures.add("positioning",
                     "README.md does not carry the canonical short description verbatim")
    if SOURCE_DISTRIBUTION_PHRASE not in collapsed:
        failures.add("positioning",
                     f"README.md does not state {SOURCE_DISTRIBUTION_PHRASE!r}")

    adopting = REPO_ROOT / "ADOPTING.md"
    if adopting.is_file():
        if SOURCE_DISTRIBUTION_PHRASE not in " ".join(read_text(adopting).split()):
            failures.add("positioning",
                         f"ADOPTING.md does not state {SOURCE_DISTRIBUTION_PHRASE!r}")


def check_documentation_truth(failures: Failures) -> None:
    """WO-PL-022 B.3 item 6: the public documentation-truth rule.

    The missing-example, missing-provider-envelope-disclosure, and
    unsupported-full-enforcement-claim cases are implemented in this slice.
    Stale candidate-inventory is a separate case for a later slice.

    The provider-envelope check is a semantic minimal invariant, not a pin on
    one editorial sentence: B.3 item 4 requires foregrounding that WO-PL-017
    through WO-PL-020 ran in Codex outside the installed Claude hook and were
    instruction-bounded, so the example must name both the alternate provider
    and the instruction-bounded nature of that evidence, in any wording.

    The unsupported-evidence-claims check is likewise a narrow semantic
    marker, not exhaustive natural-language validation: the accepted
    aggregate record (`governance/decisions/DR-002.md`; the per-order
    Declared/enforced/unenforced rows in `governance/STATE.md`, e.g. 8 / 0 / 8
    for WO-PL-016) is that zero whole surfaces qualified as mechanically
    enforced in every counted pilot order. A claim inverting that — asserting
    zero UNenforced boundaries, i.e. full mechanical enforcement — is flagged.
    Truthful discussion of the real, partial, per-channel native enforcement
    (e.g. the read/write tool controls) does not use that inverted phrasing
    and is unaffected.
    """
    if not PILOT_EXAMPLE.is_file():
        failures.add(
            "doc-truth",
            f"missing evidence-backed public pilot example: {rel(PILOT_EXAMPLE)}")
        return
    text = read_text(PILOT_EXAMPLE).lower()
    if "codex" not in text or "instruction-bounded" not in text:
        failures.add(
            "doc-truth",
            f"{rel(PILOT_EXAMPLE)} does not disclose the provider envelope "
            "(WO-PL-017 through WO-PL-020 ran in Codex, outside the "
            "installed Claude hook, and were instruction-bounded)")
    if re.search(r"zero\s+unenforced", text) or re.search(
            r"no\s+unenforced\s+boundar", text):
        failures.add(
            "doc-truth",
            f"{rel(PILOT_EXAMPLE)} makes an unsupported evidence claim: the "
            "accepted aggregate record (DR-002) shows zero whole surfaces "
            "qualified as mechanically enforced in every counted order, not "
            "zero unenforced boundaries")


# --------------------------------------------------------------------------
# Templates against doctrine appendices
# --------------------------------------------------------------------------

APPENDIX_HEADING = re.compile(r"^## APPENDIX ([A-E])\. (.+)$")


def doctrine_appendices() -> dict:
    lines = read_text(DOCTRINE).splitlines()

    end = len(lines)
    while end > 0 and not lines[end - 1].strip():
        end -= 1
    if end > 0 and re.match(r"^\*Revision .*\*$", lines[end - 1].strip()):
        end -= 1
        while end > 0 and not lines[end - 1].strip():
            end -= 1
        if end > 0 and lines[end - 1].strip() == "---":
            end -= 1

    starts = [(i, m) for i, line in enumerate(lines[:end])
              if (m := APPENDIX_HEADING.match(line))]

    appendices = {}
    for position, (index, match) in enumerate(starts):
        stop = starts[position + 1][0] if position + 1 < len(starts) else end
        body = lines[index + 1:stop]
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()
        appendices[match.group(1)] = {"title": match.group(2).strip(), "body": body}
    return appendices


def check_templates(control: dict, failures: Failures) -> None:
    revision = control["revision"] or "?"
    note = (f"_Extracted verbatim from DOCTRINE.md rev {revision}. "
            "Do not edit here; templates change only when the doctrine does._")
    appendices = doctrine_appendices()

    for letter, filename in sorted(TEMPLATE_FILES.items()):
        path = REPO_ROOT / "templates" / filename
        if not path.is_file():
            continue
        if letter not in appendices:
            failures.add("template", f"DOCTRINE.md has no APPENDIX {letter}")
            continue

        lines = read_text(path).splitlines()
        while lines and not lines[-1].strip():
            lines.pop()
        if not lines:
            failures.add("template", f"{rel(path)} is empty")
            continue

        expected_heading = f"# Doctrine Appendix {letter}. {appendices[letter]['title']}"
        if lines[0].strip() != expected_heading:
            failures.add(
                "template",
                f"{rel(path)} heading is {lines[0].strip()!r}, expected {expected_heading!r}")
            continue
        if lines[-1].strip() != note:
            failures.add(
                "template",
                f"{rel(path)} extraction note is {lines[-1].strip()!r}, expected {note!r}")
            continue

        body = lines[1:-1]
        while body and not body[0].strip():
            body.pop(0)
        while body and not body[-1].strip():
            body.pop()

        if body != appendices[letter]["body"]:
            failures.add(
                "template",
                f"{rel(path)} body differs from DOCTRINE.md APPENDIX {letter}")


# --------------------------------------------------------------------------
# Qualification cross-references (8.4.3 circularity vs 8.4.4 qualification)
# --------------------------------------------------------------------------

CLAUSE_START = re.compile(r"^D\.\d")


def clause_blocks(lines: list[str], prefix: str) -> list[str]:
    """Return each clause beginning with `prefix`, joined with its wrapped
    continuation lines, so a reference on a second line is still seen."""
    blocks = []
    current = None
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(prefix):
            if current is not None:
                blocks.append(" ".join(current))
            current = [stripped]
            continue
        if current is None:
            continue
        if not stripped or CLAUSE_START.match(stripped) or stripped.startswith("```"):
            blocks.append(" ".join(current))
            current = None
            continue
        current.append(stripped)
    if current is not None:
        blocks.append(" ".join(current))
    return blocks


def check_qualification_references(failures: Failures) -> None:
    doctrine_lines = read_text(DOCTRINE).splitlines()

    d5_blocks = clause_blocks(doctrine_lines, "D.5 ")
    if not d5_blocks:
        failures.add("qualification", "DOCTRINE.md has no D.5 clause")
    for block in d5_blocks:
        if "8.4.3" in block:
            failures.add("qualification",
                         "DOCTRINE.md D.5 still points qualification status at 8.4.3")
        if "8.4.4" not in block:
            failures.add("qualification", "DOCTRINE.md D.5 does not cite 8.4.4")

    rows = [l for l in doctrine_lines if l.strip().startswith("| 9.2.8 ")]
    if not rows:
        failures.add("qualification", "DOCTRINE.md has no 9.2.8 metric row")
    for row in rows:
        if "8.4.3" in row:
            failures.add("qualification", "DOCTRINE.md 9.2.8 still points at 8.4.3")
        if "8.4.4" not in row:
            failures.add("qualification", "DOCTRINE.md 9.2.8 does not cite 8.4.4")

    template = REPO_ROOT / "templates" / "D-adoption-record.md"
    if template.is_file():
        template_blocks = clause_blocks(read_text(template).splitlines(), "D.5 ")
        if not template_blocks:
            failures.add("qualification", f"{rel(template)} has no D.5 clause")
        for block in template_blocks:
            if "8.4.3" in block:
                failures.add("qualification",
                             f"{rel(template)} D.5 still points at 8.4.3")
            if "8.4.4" not in block:
                failures.add("qualification", f"{rel(template)} D.5 does not cite 8.4.4")

    # The circularity rule itself must still be present at 8.4.3.
    if not any(l.strip().startswith("8.4.3 ") for l in doctrine_lines):
        failures.add("qualification", "DOCTRINE.md no longer defines clause 8.4.3")
    if not any(l.strip().startswith("8.4.4 ") for l in doctrine_lines):
        failures.add("qualification", "DOCTRINE.md no longer defines clause 8.4.4")


# --------------------------------------------------------------------------
# Adapter README coverage vs adapter constants
# --------------------------------------------------------------------------

COVERAGE_LINE = re.compile(r"^([A-Z_]+)\s*=\s*(.*)$")
COVERAGE_KEYS = ("FILE_EDIT_TOOLS", "SHELL_TOOLS", "READ_TOOLS", "NETWORK_TOOLS",
                 "NONMUTATING_TOOLS", "UNSUPPORTED_MUTATION_TOOLS")


def load_adapter():
    spec = importlib.util.spec_from_file_location("_wall_check", ADAPTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def readme_coverage() -> dict:
    declared = {}
    for line in read_text(ADAPTER_README).splitlines():
        match = COVERAGE_LINE.match(line.strip())
        if match and match.group(1) in COVERAGE_KEYS:
            names = [n.strip() for n in match.group(2).split(",") if n.strip()]
            declared[match.group(1)] = frozenset(names)
    return declared


def check_adapter_coverage(failures: Failures) -> None:
    if not ADAPTER.is_file() or not ADAPTER_README.is_file():
        return
    try:
        module = load_adapter()
    except Exception as exc:  # noqa: BLE001
        failures.add("coverage", f"adapter will not import: {type(exc).__name__}: {exc}")
        return

    declared = readme_coverage()
    for key in COVERAGE_KEYS:
        actual = getattr(module, key, None)
        if actual is None:
            failures.add("coverage", f"adapter defines no {key}")
            continue
        if key not in declared:
            failures.add("coverage", f"adapter README declares no {key}")
            continue
        if frozenset(actual) != declared[key]:
            missing = sorted(frozenset(actual) - declared[key])
            extra = sorted(declared[key] - frozenset(actual))
            detail = []
            if missing:
                detail.append(f"in adapter but not README: {', '.join(missing)}")
            if extra:
                detail.append(f"in README but not adapter: {', '.join(extra)}")
            failures.add("coverage", f"{key} disagrees; " + "; ".join(detail))


# --------------------------------------------------------------------------
# Forbidden package paths
# --------------------------------------------------------------------------

def scan_paths() -> list[Path]:
    results = []
    for path in REPO_ROOT.rglob("*"):
        relative = path.relative_to(REPO_ROOT)
        if any(part in SCAN_EXCLUDED_DIRS for part in relative.parts):
            continue
        if path.is_file():
            results.append(path)
    return sorted(results)


def check_forbidden_paths(failures: Failures) -> None:
    for path in scan_paths():
        relative = path.relative_to(REPO_ROOT)
        for part in relative.parts[:-1]:
            if part.lower() in FORBIDDEN_DIR_NAMES:
                failures.add("forbidden-path",
                             f"{relative.as_posix()} lies under a forbidden '{part}' directory")
        if path.suffix.lower() == ".zip":
            failures.add("forbidden-path",
                         f"{relative.as_posix()} is a nested archive inside the repository")
        for pattern in FORBIDDEN_NAME_PATTERNS:
            if pattern.match(path.name):
                failures.add("forbidden-path",
                             f"{relative.as_posix()} is a loose alternate package filename")


# --------------------------------------------------------------------------
# Built archive
# --------------------------------------------------------------------------

def check_archive(archive_path: Path, failures: Failures,
                  *, projection: bool = False) -> None:
    if not archive_path.is_file():
        failures.add("archive", f"archive not found: {archive_path}")
        return
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()

    if not names:
        failures.add("archive", "archive is empty")
        return

    roots = {name.split("/", 1)[0] for name in names}
    if roots != {"plumbline"}:
        failures.add("archive",
                     f"archive must contain exactly one top-level directory "
                     f"'plumbline/', found: {', '.join(sorted(roots))}")

    # Governance packaging gate.
    for name in names:
        if "/" not in name.rstrip("/"):
            failures.add("archive", f"{name} sits at the archive root outside plumbline/")

    for name in names:
        parts = name.split("/")
        for part in parts[1:-1]:
            if part.lower() in FORBIDDEN_DIR_NAMES:
                failures.add("archive", f"{name} lies under a forbidden '{part}' directory")
        leaf = parts[-1]
        if leaf.lower().endswith(".zip"):
            failures.add("archive", f"{name} is a nested archive")
        for pattern in FORBIDDEN_NAME_PATTERNS:
            if pattern.match(leaf):
                failures.add("archive", f"{name} is a loose alternate package filename")
        if parts[1:2] in (["bootstrap"], ["dist"]):
            failures.add("archive", f"{name} should have been excluded from the distribution")
        if leaf.startswith(("REMEDIATION-REPORT", "REMEDIATION-INVENTORY")):
            failures.add("archive", f"{name} should have been excluded from the distribution")

    if "plumbline/MANIFEST.sha256" not in names:
        failures.add("archive", "archive has no MANIFEST.sha256")

    if projection:
        if len(names) != len(set(names)):
            failures.add("projection", "projection archive has a duplicate member")
        for name in names:
            if name.endswith("/"):
                failures.add("projection",
                             "projection archive contains a directory entry")
                continue
            if not name.startswith("plumbline/"):
                continue
            relative = name[len("plumbline/"):]
            if ("\\" in relative or
                    any(part in ("", ".", "..") for part in relative.split("/"))):
                failures.add("projection",
                             "projection archive has an unsafe member path")
        projection_members = [
            name for name in names
            if name.startswith("plumbline/") and not name.endswith("/")
        ]
        if len(projection_members) != len(set(projection_members)):
            failures.add("projection", "projection archive has a duplicate member")
        for name in projection_members:
            relative = name[len("plumbline/"):]
            if ("\\" in relative or
                    any(part in ("", ".", "..") for part in relative.split("/"))):
                failures.add("projection",
                             "projection archive has an unsafe member path")
        relative_names = {
            name[len("plumbline/"):] for name in projection_members
        }
        for relative in relative_names:
            if any(relative == prefix[:-1] or relative.startswith(prefix)
                   for prefix in PROJECTION_DENIED_PREFIXES):
                failures.add("projection",
                             f"projection archive contains a private-only path: {relative}")
        with zipfile.ZipFile(archive_path) as projection_archive:
            for info in projection_archive.infolist():
                mode = (info.external_attr >> 16) & 0xFFFF
                if stat.S_IFMT(mode) == stat.S_IFLNK:
                    failures.add("projection",
                                 "projection archive contains a symlink member")
            validate_projection_records(
                lambda relative: projection_archive.read(f"plumbline/{relative}"),
                relative_names, failures, "archive")
            allowlist_name = "plumbline/projection/public-files.txt"
            if allowlist_name in names:
                archive_entries = parse_projection_allowlist(
                    projection_archive.read(allowlist_name), failures, "archive")
                exact_members = set(archive_entries) | {
                    "PROJECTION-MANIFEST.sha256",
                    "PROJECTION-PROVENANCE.md",
                    "MANIFEST.sha256",
                }
                if relative_names != exact_members:
                    failures.add("projection",
                                 "projection archive member set differs from the allowlist")
                if "plumbline/MANIFEST.sha256" in names:
                    try:
                        distribution_lines = projection_archive.read(
                            "plumbline/MANIFEST.sha256").decode("utf-8").splitlines()
                    except UnicodeDecodeError:
                        failures.add("projection",
                                     "projection archive distribution manifest is not UTF-8")
                    else:
                        distribution_found: dict[str, str] = {}
                        distribution_order: list[str] = []
                        for line in distribution_lines:
                            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
                            if match is None:
                                failures.add(
                                    "projection",
                                    "projection archive distribution manifest is malformed")
                                continue
                            digest, relative = match.groups()
                            if relative in distribution_found:
                                failures.add(
                                    "projection",
                                    "projection archive distribution manifest has a duplicate path")
                            distribution_found[relative] = digest
                            distribution_order.append(relative)
                        expected_payloads = exact_members - {"MANIFEST.sha256"}
                        if (distribution_order != sorted(distribution_order) or
                                set(distribution_found) != expected_payloads):
                            failures.add(
                                "projection",
                                "projection archive distribution manifest coverage differs")
                        for relative, digest in distribution_found.items():
                            member = f"plumbline/{relative}"
                            if member not in names:
                                continue
                            actual = hashlib.sha256(
                                projection_archive.read(member)).hexdigest()
                            if actual != digest:
                                failures.add(
                                    "projection",
                                    "projection archive distribution manifest digest mismatch")

    # Transient live-work state (WO-PL-015). Same relative-path rule as the
    # source and build modes, applied to archive member names once their
    # `plumbline/` archive root is stripped.
    if BUILDER.is_file():
        try:
            builder = load_builder()
        except Exception as exc:  # noqa: BLE001
            failures.add("transient-release-state",
                         f"the builder will not import, so the archive "
                         f"cannot be checked for transient release state: "
                         f"{type(exc).__name__}: {exc}")
        else:
            for name in names:
                if name.endswith("/") or not name.startswith("plumbline/"):
                    continue
                relative = name[len("plumbline/"):]
                if builder.is_transient_release_path(relative):
                    failures.add(
                        "transient-release-state",
                        f"{name} is transient live-work state and must "
                        "never enter a release archive")

    # Charter kill list: no release archive carries local absolute paths or
    # machine-specific data. A build path baked into a shipped config is a
    # silent breakage for every recipient.
    #
    # Scoped to paths specific to THIS machine: the repository's own absolute
    # location and the building user's home directory. Deliberate fixture
    # paths ("C:/Windows/system.ini"), regex sources, and historical evidence
    # naming some OTHER machine are not machine-specific data and are not
    # flagged.
    #
    # RFI-15: every shipped entry is scanned. `archive/**` formerly carried a
    # blanket exemption, scoped to the historical v0.1 material at a time when
    # nothing else under `archive/` shipped. The Owner's RFI-09 disposition
    # made `archive/pre-adoption-bootstrap/` a deliberate shipping target,
    # which turned that exemption into an unchecked subtree. No packageable
    # subtree is exempt merely because it is historical.
    machine_paths = {str(REPO_ROOT), REPO_ROOT.as_posix()}
    home = Path.home()
    machine_paths |= {str(home), home.as_posix()}
    machine_paths = {p for p in machine_paths if len(p) > 3}

    with zipfile.ZipFile(archive_path) as handle:
        for name in names:
            if name.endswith("/"):
                continue
            if not name.lower().endswith(
                    (".json", ".md", ".py", ".sh", ".txt", ".yml", ".yaml", ".toml")):
                continue
            text = handle.read(name).decode("utf-8", errors="ignore")
            for needle in machine_paths:
                if machine_path_occurs(text, needle):
                    failures.add(
                        "archive",
                        f"{name} contains the build machine's own path "
                        f"({needle}); the charter kill list forbids "
                        "machine-specific data in a release archive")
                    break
    state = governance_state(failures)
    claude_entries = sorted(n[len("plumbline/"):] for n in names
                            if n.startswith("plumbline/.claude/"))
    if projection:
        if claude_entries:
            failures.add(
                "archive",
                "a public projection must not carry an active provider installation: "
                + ", ".join(claude_entries))
    elif state == PRE_ADOPTION:
        if claude_entries:
            failures.add("archive",
                         "plumbline/.claude/ is in the archive while the "
                         "repository is pre-adoption; the enforcement "
                         "installation ships only after adoption: "
                         + ", ".join(claude_entries))
    else:
        for entry in claude_entries:
            if entry not in PACKAGED_CLAUDE_FILES:
                failures.add("archive",
                             f"plumbline/{entry} must never be packaged; the "
                             "post-adoption archive carries only "
                             + ", ".join(sorted(PACKAGED_CLAUDE_FILES)))
        for required in sorted(PACKAGED_CLAUDE_FILES):
            if required not in claude_entries:
                failures.add("archive",
                             f"the repository is adopted but plumbline/{required} "
                             "is missing from the archive")
    for forbidden in NEVER_PACKAGED_CLAUDE:
        if f"plumbline/{forbidden}" in names:
            failures.add("archive", f"plumbline/{forbidden} must never be packaged")
    governance_entries = [n for n in names
                          if n.startswith(f"plumbline/{GOVERNANCE}/")]
    if state == PRE_ADOPTION:
        if governance_entries:
            failures.add(
                "archive",
                f"{len(governance_entries)} governance/ entries are in the archive "
                "while the repository is pre-adoption; the unratified instance "
                "must be excluded (e.g. " + governance_entries[0] + ")")
    else:
        if f"plumbline/{GOVERNANCE}/decisions/DR-001.md" not in names:
            failures.add("archive",
                         "the repository is adopted but the archive carries no "
                         "governance/decisions/DR-001.md")
    for name in names:
        leaf = name.split("/")[-1]
        if leaf in NEVER_PACKAGED_NAMES:
            failures.add("archive",
                         f"{name} must never enter a release archive")
    with zipfile.ZipFile(archive_path) as archive:
        for name in governance_entries:
            if not name.endswith(".md"):
                continue
            text = archive.read(name).decode("utf-8", errors="replace")
            if marked_proposed(text):
                failures.add("archive",
                             f"{name} is still marked PROPOSED and must not ship")

    # RFI-05 resolution: the governed source distribution retains Plumbline's
    # own charter as an inspectable self-hosting example. A clean-history
    # public projection replaces those private-instance instructions with the
    # exact public-only notice enforced by the projection builder/checker.
    if not projection and "plumbline/CLAUDE.md" not in names:
        failures.add("archive",
                     "archive is missing plumbline/CLAUDE.md; the source "
                     "distribution retains Plumbline's operating charter")

    control = document_control()
    ratified = (control["status"] or "").strip().lower() == "ratified" and \
        (control["dc2_ratified"] or "").strip().lower() in ("yes", "ratified")
    stem = archive_path.stem.lower()
    has_candidate_marker = "rc" in stem.split("-") or "candidate" in stem
    if not ratified and not has_candidate_marker:
        failures.add("archive",
                     f"{archive_path.name} carries no candidate marker while DC.1 "
                     f"records {control['status']!r}")
    if ratified and has_candidate_marker:
        failures.add("archive",
                     f"{archive_path.name} carries a candidate marker while DC.1 and "
                     "DC.2 both record ratification; a ratified release is not an rc")


# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the Plumbline distribution.")
    parser.add_argument("--archive", help="also inspect a built distribution archive")
    parser.add_argument("--projection", action="store_true",
                        help="validate explicit clean-history projection mode")
    args = parser.parse_args(argv)

    failures = Failures()
    control = document_control()

    if args.projection:
        check_projection_records(failures)

    check_required_files(failures, projection=args.projection)
    check_license_records(failures)
    check_license_mechanization(failures)
    check_bundle_copies(failures)
    check_self_hosting_segregation(failures)
    check_governance_packaging(failures)
    check_hook_registration(failures)
    check_line_endings(failures)
    check_transient_release_state(failures)
    check_source_machine_paths(failures)
    check_positioning(failures)
    check_documentation_truth(failures)
    check_templates(control, failures)
    check_qualification_references(failures)
    check_markers(control, failures)
    if not args.projection:
        check_v01_determination(failures)
        check_archive_provenance(failures)
    check_adapter_coverage(failures)
    check_forbidden_paths(failures)

    if args.archive:
        archive_path = Path(args.archive)
        if not archive_path.is_absolute():
            archive_path = REPO_ROOT / archive_path
        check_archive(archive_path, failures, projection=args.projection)

    revision = control["revision"]
    status = control["status"]
    print(f"doctrine revision {revision}, DC.1 status {status!r}, "
          f"DC.2 ratified {control['dc2_ratified']!r}")
    if args.archive:
        print(f"archive inspected: {args.archive}")

    if failures:
        print(f"\nFAIL: {len(failures.items)} problem(s)\n")
        for item in failures.items:
            print(f"  {item}")
        return 1
    print("\nOK: all distribution checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
