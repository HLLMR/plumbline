#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Deterministically check Writwall's tracked-file license coverage."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    print(
        "ERROR: checks/check_licenses.py requires Python 3.11 or newer "
        "(the standard-library tomllib module is unavailable).",
        file=sys.stderr,
    )
    raise SystemExit(2) from None


SPDX_ID_RE = re.compile(
    rb"(?m)^\s*#\s*SPDX-License-Identifier:\s*([^\r\n]+?)\s*$"
)
SPDX_COPYRIGHT_RE = re.compile(rb"(?m)^\s*#\s*SPDX-FileCopyrightText:\s*\S")
SPDX_TEMPLATE_CONTROL_RE = re.compile(
    rb"<<(?:beginOptional|endOptional|var);"
)
SUPPORTED_IDS = {"CC-BY-4.0", "CC0-1.0", "MIT-0", "Apache-2.0"}
ALLOWED_EXCLUSIONS = {"LICENSE", "LICENSES/**", "REUSE.toml", "dist/**"}
CONTENT_READ_DENIED = ["governance/history/**", "archive/**"]


def tracked_files(root: Path, include_untracked: bool = False) -> list[str]:
    if include_untracked or not (root / ".git").exists():
        skipped = {".git", "__pycache__", ".pytest_cache"}
        return sorted(
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file() and not any(part in skipped for part in path.parts)
        )
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError("git ls-files failed")
    return sorted(
        item.decode("utf-8", errors="surrogateescape")
        for item in result.stdout.split(b"\0") if item
    )


def matches(path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        expression = ""
        index = 0
        while index < len(pattern):
            if pattern[index:index + 2] == "**":
                expression += ".*"
                index += 2
            elif pattern[index] == "*":
                expression += "[^/]*"
                index += 1
            elif pattern[index] == "?":
                expression += "[^/]"
                index += 1
            else:
                expression += re.escape(pattern[index])
                index += 1
        if re.fullmatch(expression, path):
            return True
    return False


def load_metadata(root: Path) -> tuple[list[dict], list[dict]]:
    with (root / "REUSE.toml").open("rb") as handle:
        data = tomllib.load(handle)
    return data.get("annotations", []), data.get("exclusions", [])


def header_region(path: Path) -> bytes:
    region: list[bytes] = []
    for index, line in enumerate(path.read_bytes().splitlines()[:20]):
        if index == 0 and line.startswith(b"#!"):
            region.append(line)
        elif not line.strip() or line.lstrip().startswith(b"#"):
            region.append(line)
        else:
            break
    return b"\n".join(region)


def header_identifier(path: Path) -> str | None:
    match = SPDX_ID_RE.search(header_region(path))
    return match.group(1).decode("utf-8", errors="replace") if match else None


def expected_header(rel: str) -> str | None:
    if rel == "init.sh":
        return "MIT-0"
    if rel.endswith(".py") and (
        rel.startswith("adapters/")
        or rel.startswith(".claude/hooks/")
        or rel.startswith("skills/writwall-adopt/assets/adapters/")
    ):
        return "MIT-0"
    if rel.endswith(".py") and (
        rel.startswith("scripts/")
        or rel.startswith("checks/")
        or rel.startswith("tests/")
        or rel.startswith("skills/writwall-adopt/assets/checks/")
    ):
        return "Apache-2.0"
    return None


def check(root: Path, include_untracked: bool = False) -> list[str]:
    annotations, exclusions = load_metadata(root)
    findings: list[str] = []
    used_ids: set[str] = set()
    for item in exclusions:
        for pattern in item.get("path", []):
            if pattern not in ALLOWED_EXCLUSIONS:
                findings.append(f"[exclusion] unknown exclusion pattern {pattern}")
            if not str(item.get("reason", "")).strip():
                findings.append(f"[exclusion] {pattern} has no reason")
    root_license = root / "LICENSE"
    cc_by_code = root / "LICENSES" / "CC-BY-4.0.txt"
    legal_code_paths = [
        root_license,
        *(root / "LICENSES" / f"{identifier}.txt"
          for identifier in sorted(SUPPORTED_IDS)),
    ]
    for legal_code in legal_code_paths:
        if (legal_code.is_file()
                and SPDX_TEMPLATE_CONTROL_RE.search(legal_code.read_bytes())):
            relative = legal_code.relative_to(root).as_posix()
            findings.append(
                f"[legal-code] {relative} contains SPDX template controls"
            )
    if root_license.is_file() and cc_by_code.is_file():
        if root_license.read_bytes() != cc_by_code.read_bytes():
            findings.append(
                "[legal-code] LICENSE differs from LICENSES/CC-BY-4.0.txt"
            )
    for rel in tracked_files(root, include_untracked):
        if any(matches(rel, item.get("path", [])) for item in exclusions):
            continue
        path = root / rel
        content_read_allowed = not matches(rel, CONTENT_READ_DENIED)
        identifier = header_identifier(path) if content_read_allowed else None
        required_header = expected_header(rel)
        if content_read_allowed and rel.endswith(".md") and identifier is not None:
            findings.append(
                f"[header] {rel} must use REUSE.toml, not an in-file SPDX header"
            )
        if required_header is not None and identifier is None:
            findings.append(
                f"[header] {rel} must carry in-file {required_header}"
            )
        elif required_header is not None and identifier != required_header:
            findings.append(
                f"[header] {rel} carries {identifier}, expected {required_header}"
            )
        if required_header is not None and not SPDX_COPYRIGHT_RE.search(header_region(path)):
            findings.append(f"[header] {rel} lacks SPDX-FileCopyrightText")
        identifiers = {
            item.get("SPDX-License-Identifier")
            for item in annotations
            if matches(rel, item.get("path", []))
        }
        identifiers.discard(None)
        if identifier is not None:
            identifiers.add(identifier)
        if len(identifiers) > 1:
            used_ids.update(identifiers & SUPPORTED_IDS)
            joined = ", ".join(sorted(identifiers))
            findings.append(
                f"[conflict] {rel} resolves to multiple licenses: {joined}"
            )
            continue
        identifier = next(iter(identifiers), None)
        if identifier is None:
            findings.append(f"[coverage] {rel} has no license declaration")
        elif identifier not in SUPPORTED_IDS:
            findings.append(
                f"[identifier] {rel} uses unsupported SPDX identifier {identifier}"
            )
        else:
            used_ids.add(identifier)
    for identifier in sorted(used_ids):
        legal_code = root / "LICENSES" / f"{identifier}.txt"
        if not legal_code.is_file():
            findings.append(
                f"[legal-code] {identifier} has no canonical "
                f"LICENSES/{identifier}.txt"
            )
    for identifier in sorted(SUPPORTED_IDS - used_ids):
        legal_code = root / "LICENSES" / f"{identifier}.txt"
        if not legal_code.is_file():
            findings.append(
                f"[legal-code] required LICENSES/{identifier}.txt is missing"
            )
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--all-files", action="store_true",
        help="scan the complete source tree, including untracked packageable files",
    )
    args = parser.parse_args(argv)
    try:
        findings = check(args.repo_root.resolve(), args.all_files)
    except (OSError, RuntimeError, tomllib.TOMLDecodeError) as exc:
        print(f"FAIL: [metadata] {exc}")
        return 1
    if findings:
        print(f"FAIL: {len(findings)} license problem(s)")
        for finding in findings:
            print(f"  {finding}")
        return 1
    print("OK: all tracked project files have deterministic license coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
