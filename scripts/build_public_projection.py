# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Build a deterministic clean-history Writwall projection candidate."""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOWLIST = Path("projection/public-files.txt")
MANIFEST = Path("PROJECTION-MANIFEST.sha256")
PROVENANCE = Path("PROJECTION-PROVENANCE.md")
FULL_ID = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])",
                     re.IGNORECASE)
PROJECTION_NOTE = ("Projection note: archive and Git-history recoverability statements "
                   "in this record apply only to the private governed source.")
PRIVATE_RETAINED_REFERENCE_NOTE = (
    "(private governed-source reference, not present in this candidate)")
TARGET_PROJECT_REFERENCE_NOTE = (
    "(target-project path, not a candidate member)")
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
SOURCE_DISTRIBUTION_COMMAND = b"python -B checks/check_distribution.py"
PROJECTION_DISTRIBUTION_COMMAND = (
    b"python -B checks/check_distribution.py --projection")
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

    Markdown targets may be root-relative or nested (`./` or repeated `../`);
    the returned value is normalized to the candidate-root-relative suffix.
    Plain prose is intentionally limited to file-like paths so ordinary terms
    such as ``archive/history`` and trailing-slash directory descriptions do
    not become false links.
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
STATE_RELATIVE = "governance/STATE.md"
STATE_SNAPSHOT_NOTE = (
    "Snapshot note: this record is a snapshot of the private governed source "
    "at the source commit named in `PROJECTION-PROVENANCE.md`. Push, "
    "publication, visibility, and queued-work statements below describe that "
    "checkpoint, not the current public copy.")
TARGET_PROJECT_REFERENCE_FILES = frozenset({
    "migration-guides/0.1-to-0.6.md",
    "skills/writwall-adopt/references/migration-guides/0.1-to-0.6.md",
})
PRIVATE_EVIDENCE_REDACTION_FILES = frozenset({
    "governance/LOG.md",
})
PRIVATE_EVIDENCE_REDACTION = "[private governed-source identifier omitted]"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_private_input(path: Path) -> bytes:
    try:
        raw = path.read_bytes()
    except OSError:
        raise SystemExit("private pattern input is unavailable") from None
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        raise SystemExit("private pattern input is not UTF-8") from None
    return raw


def parse_private_patterns(raw: bytes) -> list[str]:
    return sorted(
        {
            line.strip()
            for line in raw.decode("utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        },
        key=lambda value: (-len(value), value.casefold()),
    )


def redact_private_evidence(relative: str, data: bytes,
                            patterns: list[str]) -> bytes:
    if relative not in PRIVATE_EVIDENCE_REDACTION_FILES:
        return data
    text = data.decode("utf-8")
    for pattern in patterns:
        text = re.sub(
            re.escape(pattern), PRIVATE_EVIDENCE_REDACTION, text,
            flags=re.IGNORECASE)
    return text.encode("utf-8")


def read_allowlist(source_root: Path) -> tuple[list[str], bytes]:
    raw = (source_root / ALLOWLIST).read_bytes()
    entries = [line.strip() for line in raw.decode("utf-8").splitlines()
               if line.strip()]
    if len(entries) != len(set(entries)):
        raise SystemExit("projection allowlist contains a duplicate entry")
    if entries != sorted(entries):
        raise SystemExit("projection allowlist is not sorted")
    for entry in entries:
        candidate = Path(entry)
        if (candidate.is_absolute() or "\\" in entry or
                any(part in ("", ".", "..") for part in entry.split("/"))):
            raise SystemExit(f"unsafe projection allowlist path: {entry!r}")
    return entries, raw


def transform_retained_references(relative: str, data: bytes,
                                  candidate_paths: set[str]) -> bytes:
    if relative in PRIVATE_RETAINED_REFERENCE_FILES:
        note = PRIVATE_RETAINED_REFERENCE_NOTE
    elif relative in TARGET_PROJECT_REFERENCE_FILES:
        note = TARGET_PROJECT_REFERENCE_NOTE
    else:
        return data

    text = data.decode("utf-8")
    transformed: list[str] = []
    for line in text.splitlines(keepends=True):
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


def transform_contributing(data: bytes) -> bytes:
    """Render the context-specific distribution command in candidate bytes."""
    source_pattern = re.compile(
        rb"(?m)^" + re.escape(SOURCE_DISTRIBUTION_COMMAND) + rb"(?=\r?$)")
    projection_pattern = re.compile(
        rb"(?m)^" + re.escape(PROJECTION_DISTRIBUTION_COMMAND) + rb"(?=\r?$)")
    source_count = len(source_pattern.findall(data))
    projection_count = len(projection_pattern.findall(data))
    if source_count == 1 and projection_count == 0:
        return source_pattern.sub(PROJECTION_DISTRIBUTION_COMMAND, data, count=1)
    if source_count == 0 and projection_count == 1:
        return data
    else:
        raise SystemExit(
            "CONTRIBUTING.md must carry exactly one context-valid distribution command")


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


def state_snapshot_bytes(data: bytes) -> bytes:
    if STATE_SNAPSHOT_NOTE.encode("utf-8") in data:
        return data
    return (f"> **{STATE_SNAPSHOT_NOTE}**\n\n".encode("utf-8") + data)


def provenance_bytes(source_root: Path, output: Path, entries: list[str],
                     allowlist_raw: bytes) -> bytes:
    identifiers: dict[str, set[str]] = {}
    for relative in entries:
        path = output / relative
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
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


def build(source_root: Path, output: Path, private_pattern_file: Path) -> None:
    source_root = source_root.resolve()
    output = output.resolve()
    private_raw = read_private_input(private_pattern_file)
    private_patterns = parse_private_patterns(private_raw)
    if output == source_root or source_root in output.parents:
        raise SystemExit("output must be outside the source root")
    if output.exists() and any(output.iterdir()):
        raise SystemExit("output directory must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    entries, allowlist_raw = read_allowlist(source_root)
    candidate_paths = set(entries)
    for relative in entries:
        source = source_root / relative
        target = output / relative
        if source.is_symlink():
            raise SystemExit(f"allowlisted source is a symlink: {relative}")
        if not source.is_file() or source_root not in source.resolve().parents:
            raise SystemExit(f"allowlisted source is missing or unsafe: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        if relative == "CLAUDE.md":
            data = PUBLIC_CLAUDE_BYTES
        if relative == CONTRIBUTING_RELATIVE:
            data = transform_contributing(data)
        if (relative.endswith(".md")
                and b"recoverable from Git history" in data
                and PROJECTION_NOTE.encode("utf-8") not in data):
            data = (f"> **{PROJECTION_NOTE}**\n\n".encode("utf-8") + data)
        if relative.endswith(".md"):
            data = transform_retained_references(relative, data, candidate_paths)
        data = redact_private_evidence(relative, data, private_patterns)
        if relative == STATE_RELATIVE:
            data = state_snapshot_bytes(data)
        target.write_bytes(data)
    (output / PROVENANCE).write_bytes(
        provenance_bytes(source_root, output, entries, allowlist_raw))
    payloads = [*entries, PROVENANCE.as_posix()]
    manifest_lines = []
    for relative in sorted(payloads):
        digest = sha256_bytes((output / relative).read_bytes())
        manifest_lines.append(f"{digest}  {relative}")
    (output / MANIFEST).write_text(
        "\n".join(manifest_lines) + "\n", encoding="utf-8", newline="\n")
    print(f"OK: built public projection with {len(payloads) + 1} files")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--private-pattern-file", required=True, type=Path)
    parser.add_argument("--source-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    build(args.source_root, args.output, args.private_pattern_file)


if __name__ == "__main__":
    main()
