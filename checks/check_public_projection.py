# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Independently verify a clean-history Writwall projection candidate."""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = Path("projection/public-files.txt")
MANIFEST = "PROJECTION-MANIFEST.sha256"
PROVENANCE = "PROJECTION-PROVENANCE.md"


def machine_path_occurs(text: str, needle: str) -> bool:
    """True when an absolute host path occurs at textual path boundaries."""
    escaped = re.escape(needle)
    before = r"(?<![A-Za-z0-9_.-])"
    after = r"(?=$|[\\/\s\"'`\)\]\}>:;,.!?])"
    return re.search(before + escaped + after, text, re.IGNORECASE) is not None
FULL_ID = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])",
                     re.IGNORECASE)
PROJECTION_NOTE = ("Projection note: archive and Git-history recoverability statements "
                   "in this record apply only to the private governed source.")

# WO-PL-022 B.3 items 3 and 6: a repository-tree/inventory heading inside the
# candidate must distinguish the private governed source, the source
# distribution, and the positive-allowlist candidate the reader is actually
# looking at. This is a semantic minimal invariant, not one pinned sentence:
# any wording that names both the governed source and the candidate satisfies
# it, and legitimate normative adopter-path mentions elsewhere are untouched.
INVENTORY_HEADING_MARKER = "what is in this repository"
INVENTORY_DISTINCTION_MARKERS = ("governed source", "candidate")

# WO-PL-023 B.3.5 retained-reference integrity: a projected document may
# legitimately explain private governed-source history, but it must not
# retain a navigable-looking reference to a path the candidate omits
# (archive/, governance/history/, dist/) without truthfully marking it as
# such. A line naming an omitted path and lacking the exact note fails; the
# note transforms the prose rather than deleting the (public-safe) fact.
RETAINED_REFERENCE_NOTES = (
    "(private governed-source reference, not present in this candidate)",
    "(target-project path, not a candidate member)",
)
PUBLIC_CLAUDE_BYTES = (
    "# Public projection instructions\n\n"
    "This clean-history public copy is not Writwall's governed source and "
    "does not govern its own maintenance. No active Writwall work order or "
    "capability wall is installed here. Contributors and coding agents may "
    "make ordinary repository changes under the host platform's controls; "
    "see `CONTRIBUTING.md`. Do not represent this checkout as mechanically "
    "governed unless an Owner separately adopts and installs Writwall.\n"
).encode("utf-8")
CONTRIBUTING_RELATIVE = "CONTRIBUTING.md"
SOURCE_DISTRIBUTION_COMMAND = "python -B checks/check_distribution.py"
PROJECTION_DISTRIBUTION_COMMAND = (
    "python -B checks/check_distribution.py --projection")
OMITTED_ROOT = r"(?:archive|governance/history|governance/reports|dist)"
RETAINED_BACKTICK_TOKEN = re.compile(
    rf"`({OMITTED_ROOT}/[\w./-]*[\w])`")
RETAINED_MARKDOWN_TARGET = re.compile(
    rf"\]\(\s*<?(?:/|(?:\.\.?/)*)?({OMITTED_ROOT}/[\w./-]*[\w])"
    r"(?:[?#][^>\s)]*)?>?(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)")
RETAINED_PLAIN_FILE_TOKEN = re.compile(
    rf"(?<![`(\w./-])({OMITTED_ROOT}/(?:[\w.-]+/)*[\w-]+(?:\.[\w-]+)+)"
    r"(?![\w/-])")


def find_retained_tokens(line: str) -> list[str]:
    """Concrete omitted paths in backticks, links, or plain file references.

    Mirrors scripts/build_public_projection.py's find_retained_tokens; the
    two must agree or a candidate could pass the checker on the strength of
    a narrower pattern than the one the builder actually transformed with.
    """
    tokens = [*RETAINED_BACKTICK_TOKEN.findall(line),
              *RETAINED_MARKDOWN_TARGET.findall(line),
              *RETAINED_PLAIN_FILE_TOKEN.findall(line)]
    return list(dict.fromkeys(tokens))
PRIVATE_RETAINED_REFERENCE_FILES = frozenset({
    "CLAUDE.md",
    "decisions/DR-001.md",
    "decisions/DR-005.md",
    "governance/ADOPTION-MAPPING.md",
    "governance/LOG-denials-probes.md",
    "governance/ROUTING.md",
    "governance/decisions/DR-001.md",
    "governance/decisions/DR-005.md",
})
TARGET_PROJECT_REFERENCE_FILES = frozenset({
    "migration-guides/0.1-to-0.6.md",
    "skills/writwall-adopt/references/migration-guides/0.1-to-0.6.md",
})
STATE_RELATIVE = "governance/STATE.md"
STATE_SNAPSHOT_NOTE = (
    "Snapshot note: this record is a snapshot of the private governed source "
    "at the source commit named in `PROJECTION-PROVENANCE.md`. Push, "
    "publication, visibility, and queued-work statements below describe that "
    "checkpoint, not the current public copy.")
PRIVATE_EVIDENCE_REDACTION_FILES = frozenset({
    "governance/LOG.md",
})
PRIVATE_EVIDENCE_REDACTION = "[private governed-source identifier omitted]"


def transform_expected_private_evidence(relative: str, data: bytes,
                                        patterns: list[str]) -> bytes:
    if relative not in PRIVATE_EVIDENCE_REDACTION_FILES:
        return data
    text = data.decode("utf-8")
    for pattern in sorted(set(patterns),
                          key=lambda value: (-len(value), value.casefold())):
        text = re.sub(
            re.escape(pattern), PRIVATE_EVIDENCE_REDACTION, text,
            flags=re.IGNORECASE)
    return text.encode("utf-8")


def check_retained_references(relative: str, text: str, candidate_paths: set[str]) -> None:
    for line_no, line in enumerate(text.splitlines(), start=1):
        tokens = find_retained_tokens(line)
        unresolved = sorted({t for t in tokens if t not in candidate_paths})
        if unresolved and not any(note in line for note in RETAINED_REFERENCE_NOTES):
            fail(f"{relative}:{line_no} retains an unresolved reference to omitted "
                 f"path(s) {unresolved!r}; transform the prose or add one of the "
                 f"exact retained-reference notes {RETAINED_REFERENCE_NOTES!r}")


def transform_expected_retained_references(relative: str, data: bytes,
                                           candidate_paths: set[str]) -> bytes:
    if relative in PRIVATE_RETAINED_REFERENCE_FILES:
        note = RETAINED_REFERENCE_NOTES[0]
    elif relative in TARGET_PROJECT_REFERENCE_FILES:
        note = RETAINED_REFERENCE_NOTES[1]
    else:
        return data

    transformed: list[str] = []
    for line in data.decode("utf-8").splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = line[len(body):]
        tokens = find_retained_tokens(body)
        unresolved = {token for token in tokens if token not in candidate_paths}
        if unresolved and note not in body:
            if body.startswith("|") and body.endswith("|"):
                body = f"{body[:-1].rstrip()} {note} |"
            else:
                body = f"{body} {note}"
        transformed.append(body + ending)
    return "".join(transformed).encode("utf-8")


def transform_expected_contributing(data: bytes) -> bytes:
    """Independently derive the projection-only verification command."""
    source_pattern = re.compile(
        rb"(?m)^" + re.escape(SOURCE_DISTRIBUTION_COMMAND.encode("utf-8"))
        + rb"(?=\r?$)")
    projection_pattern = re.compile(
        rb"(?m)^" + re.escape(PROJECTION_DISTRIBUTION_COMMAND.encode("utf-8"))
        + rb"(?=\r?$)")
    source_count = len(source_pattern.findall(data))
    projection_count = len(projection_pattern.findall(data))
    if source_count == 1 and projection_count == 0:
        return source_pattern.sub(
            PROJECTION_DISTRIBUTION_COMMAND.encode("utf-8"), data, count=1)
    if source_count == 0 and projection_count == 1:
        return data
    fail("CONTRIBUTING.md lacks one context-valid distribution command")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def load_allowlist(root: Path) -> tuple[list[str], bytes]:
    raw = (root / ALLOWLIST).read_bytes()
    entries = [line.strip() for line in raw.decode("utf-8").splitlines()
               if line.strip()]
    if entries != sorted(entries) or len(entries) != len(set(entries)):
        fail("projection allowlist is not sorted and duplicate-free")
    for entry in entries:
        candidate = Path(entry)
        if (candidate.is_absolute() or "\\" in entry or
                any(part in ("", ".", "..") for part in entry.split("/"))):
            fail("projection allowlist contains an unsafe path")
    return entries, raw


def source_identity(source_root: Path) -> tuple[str, str]:
    commit = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30)
    if commit.returncode:
        return "UNAVAILABLE", "1980-01-01T00:00:00Z"
    timestamp = subprocess.run(
        ["git", "-C", str(source_root), "show", "-s", "--format=%cI", "HEAD"],
        capture_output=True, text=True, timeout=30)
    return commit.stdout.strip(), (timestamp.stdout.strip()
                                   if timestamp.returncode == 0
                                   else "1980-01-01T00:00:00Z")


def expected_provenance_bytes(source_root: Path, entries: list[str],
                              allowlist_raw: bytes,
                              patterns: list[str]) -> bytes:
    identifiers: dict[str, set[str]] = {}
    for relative in entries:
        try:
            text = expected_source_bytes(
                source_root, relative, set(entries), patterns).decode("utf-8")
        except UnicodeDecodeError:
            continue
        for identifier in FULL_ID.findall(text):
            identifiers.setdefault(identifier, set()).add(relative)
    source_commit, timestamp = source_identity(source_root)
    lines = [
        "# Projection provenance",
        "",
        "This candidate is derived from a private governed source repository.",
        "Legacy commit identifiers in projected records refer to that private",
        "source and are intentionally not resolvable from fresh public history.",
        "No private remote URL is recorded here.",
        "",
        f"- Source commit: `{source_commit}`",
        f"- Source commit time: `{timestamp}`",
        f"- Projection allowlist SHA-256: `{sha256_bytes(allowlist_raw)}`",
        "",
        "## Legacy identifier inventory",
        "",
    ]
    if identifiers:
        for identifier in sorted(identifiers):
            paths = ", ".join(f"`{path}`" for path in sorted(identifiers[identifier]))
            lines.append(f"- `{identifier}` — {paths}")
    else:
        lines.append("- None.")
    return ("\n".join(lines) + "\n").encode("utf-8")


def expected_source_bytes(source_root: Path, relative: str,
                          candidate_paths: set[str],
                          patterns: list[str]) -> bytes:
    source = source_root / relative
    if source.is_symlink() or not source.is_file():
        fail("governed source allowlist names a missing or unsafe payload")
    resolved = source.resolve()
    if source_root not in resolved.parents:
        fail("governed source allowlist names a missing or unsafe payload")
    data = source.read_bytes()
    if relative == "CLAUDE.md":
        data = PUBLIC_CLAUDE_BYTES
    if relative == CONTRIBUTING_RELATIVE:
        data = transform_expected_contributing(data)
    if (relative.endswith(".md")
            and b"recoverable from Git history" in data
            and PROJECTION_NOTE.encode("utf-8") not in data):
        data = (f"> **{PROJECTION_NOTE}**\n\n".encode("utf-8") + data)
    if relative.endswith(".md"):
        data = transform_expected_retained_references(
            relative, data, candidate_paths)
    data = transform_expected_private_evidence(relative, data, patterns)
    if (relative == STATE_RELATIVE
            and STATE_SNAPSHOT_NOTE.encode("utf-8") not in data):
        data = (f"> **{STATE_SNAPSHOT_NOTE}**\n\n".encode("utf-8") + data)
    return data


def candidate_files(root: Path) -> list[str]:
    files = []
    for path in root.rglob("*"):
        if path.is_symlink():
            fail("candidate contains a symlink")
        if path.is_file():
            files.append(path.relative_to(root).as_posix())
    return sorted(files)


def verify_manifest(root: Path, expected_payloads: list[str]) -> None:
    lines = (root / MANIFEST).read_text(encoding="utf-8").splitlines()
    found: dict[str, str] = {}
    ordered_paths = []
    for line in lines:
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if match is None:
            fail("projection manifest has a malformed line")
        digest, relative = match.groups()
        if relative in found:
            fail("projection manifest contains a duplicate path")
        found[relative] = digest
        ordered_paths.append(relative)
    if ordered_paths != sorted(ordered_paths):
        fail("projection manifest is not path-sorted")
    if sorted(found) != sorted(expected_payloads):
        fail("projection manifest coverage differs from the allowlist")
    for relative, digest in found.items():
        if sha256_bytes((root / relative).read_bytes()) != digest:
            fail("projection manifest digest mismatch")


def private_patterns(path: Path) -> tuple[list[str], str]:
    try:
        raw = path.read_bytes()
    except OSError:
        fail("private pattern input is unavailable")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail("private pattern input is not UTF-8")
    patterns = [line.strip() for line in text.splitlines()
                if line.strip() and not line.lstrip().startswith("#")]
    return patterns, sha256_bytes(raw)


def verify(root: Path, pattern_file: Path) -> None:
    root = root.resolve()
    source_root = REPO_ROOT.resolve()
    if not root.is_dir() or root.is_symlink():
        fail("candidate root is not a regular directory")
    if any(path.name == ".git" for path in root.rglob(".git")):
        fail("candidate contains inherited Git metadata")
    if any((root / relative).exists()
           for relative in ("archive", "dist", "governance/history")):
        fail("candidate contains a denied directory")
    if any(path.is_file() for path in root.rglob("*.zip")):
        fail("candidate contains a stale archive")
    entries, allowlist_raw = load_allowlist(root)
    source_entries, source_allowlist_raw = load_allowlist(source_root)
    if allowlist_raw != source_allowlist_raw or entries != source_entries:
        fail("candidate allowlist differs from the governed source allowlist")
    expected = sorted([*entries, MANIFEST, PROVENANCE])
    if candidate_files(root) != expected:
        fail("candidate contains an unknown or missing file")
    verify_manifest(root, [*entries, PROVENANCE])
    patterns, _pattern_digest = private_patterns(pattern_file)
    host_needles = {
        str(REPO_ROOT).casefold(), REPO_ROOT.as_posix().casefold(),
        str(Path.home()).casefold(), Path.home().as_posix().casefold(),
    }
    provenance_raw = (root / PROVENANCE).read_bytes()
    provenance = provenance_raw.decode("utf-8")
    if "Private-pattern input SHA-256" in provenance:
        fail("projection provenance discloses a private-pattern fingerprint")
    allow_digest = sha256_bytes(allowlist_raw)
    if f"Projection allowlist SHA-256: `{allow_digest}`" not in provenance:
        fail("projection provenance has the wrong allowlist digest")
    identifiers: dict[str, set[str]] = {}
    for relative in expected:
        try:
            text = (root / relative).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        folded = text.casefold()
        if relative == CONTRIBUTING_RELATIVE:
            command_lines = text.splitlines()
            if command_lines.count(PROJECTION_DISTRIBUTION_COMMAND) != 1:
                fail("candidate CONTRIBUTING.md lacks its exact projection-mode command")
            if SOURCE_DISTRIBUTION_COMMAND in command_lines:
                fail("candidate CONTRIBUTING.md retains the governed-source command")
        if relative in entries:
            for identifier in FULL_ID.findall(text):
                identifiers.setdefault(identifier, set()).add(relative)
        if any(pattern.casefold() in folded for pattern in patterns):
            fail("candidate contains a private disclosure pattern")
        if any(needle and machine_path_occurs(text, needle)
               for needle in host_needles):
            fail("candidate contains host-specific data")
        if (relative.startswith("governance/") and relative.endswith(".md") and
                re.search(r"^---\n.*?^status:\s*(?:ACTIVE|PROPOSED)\s*$",
                          text, re.MULTILINE | re.DOTALL)):
            fail("candidate contains an active governance transaction")
        if (relative.endswith(".md") and "recoverable from Git history" in text and
                PROJECTION_NOTE not in text):
            fail("candidate contains an unqualified public-history recoverability claim")
        if relative == STATE_RELATIVE and STATE_SNAPSHOT_NOTE not in text:
            fail("candidate STATE snapshot boundary is missing or altered")
        if (relative.endswith(".md") and INVENTORY_HEADING_MARKER in folded and
                not all(marker in folded for marker in INVENTORY_DISTINCTION_MARKERS)):
            fail("candidate contains a stale repository-inventory heading; it "
                 "must distinguish the private governed source from the "
                 "positive-allowlist candidate")
        if relative.endswith(".md"):
            check_retained_references(relative, text, set(entries))
    for identifier, paths in identifiers.items():
        inventory_line = next(
            (line for line in provenance.splitlines()
             if line.startswith(f"- `{identifier}` — ")), None)
        if inventory_line is None or any(f"`{path}`" not in inventory_line
                                         for path in paths):
            fail("candidate contains an unclassified legacy commit identifier")
    expected_provenance = expected_provenance_bytes(
        source_root, source_entries, source_allowlist_raw, patterns)
    if provenance_raw != expected_provenance:
        fail("projection provenance differs from the governed source identity/inventory")
    if "checks/check_licenses.py" in entries:
        license_result = subprocess.run(
            [sys.executable, "-B", str(root / "checks" / "check_licenses.py"),
             "--repo-root", str(root), "--all-files"],
            cwd=root, capture_output=True, text=True, timeout=120)
        if license_result.returncode:
            fail("candidate license gate failed")
    if "checks/check_distribution.py" in entries:
        distribution_result = subprocess.run(
            [sys.executable, "-B", str(root / "checks" / "check_distribution.py"),
             "--projection"],
            cwd=root, capture_output=True, text=True, timeout=300)
        if distribution_result.returncode:
            fail("candidate distribution gate failed")
    for relative in source_entries:
        if (root / relative).read_bytes() != expected_source_bytes(
                source_root, relative, set(source_entries), patterns):
            fail("candidate payload differs from the governed source payload")
    print(f"OK: public projection verified ({len(expected)} files)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--private-pattern-file", required=True, type=Path)
    args = parser.parse_args()
    verify(args.candidate, args.private_pattern_file)


if __name__ == "__main__":
    main()
