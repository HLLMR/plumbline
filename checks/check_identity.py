#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Check the current identity and classified former-identity references."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath


DEFAULT_MANIFEST = Path("identity/legacy-references.json")
DEFAULT_ALLOWLIST = Path("projection/public-files.txt")
ACCEPTED_LEDGER = Path("examples/name-clearance-ledgers/writwall-candidate.json")
FORMER_LEDGER = Path("examples/name-clearance-ledgers/plumbline-incident.json")
PRIVATE_EVIDENCE_REDACTION = "[private governed-source identifier omitted]"
PROJECTION_TRANSFORM_PATHS = {
    "private_evidence_redaction": frozenset({"governance/LOG.md"}),
}


def read_json(path: Path, failures: list[str]) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        failures.append(f"[manifest] cannot read canonical JSON: {exc}")
        return None
    if not isinstance(value, dict):
        failures.append("[manifest] top level must be an object")
        return None
    return value


def retained_paths(manifest: dict, failures: list[str]) -> dict[str, dict]:
    entries = manifest.get("retained")
    if not isinstance(entries, list):
        failures.append("[manifest] retained must be a list")
        return {}
    result: dict[str, dict] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            failures.append("[manifest] every retained entry needs a path")
            continue
        relative = entry["path"]
        parsed = PurePosixPath(relative)
        if (
            not relative
            or parsed.is_absolute()
            or ".." in parsed.parts
            or "\\" in relative
        ):
            failures.append(
                f"[manifest] retained path must be repository-relative: {relative}"
            )
        if relative in result:
            failures.append(f"[manifest] duplicate retained path: {relative}")
        if not isinstance(entry.get("context"), str) or not entry["context"].strip():
            failures.append(
                f"[manifest] retained entry needs non-empty context: {relative}"
            )
        for digest_key in ("sha256", "projection_sha256"):
            digest = entry.get(digest_key)
            if digest_key == "projection_sha256" and digest is None:
                continue
            if not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                failures.append(
                    f"[manifest] retained entry has invalid {digest_key}: {relative}"
                )
        transform = entry.get("projection_transform")
        if transform is not None:
            allowed_paths = PROJECTION_TRANSFORM_PATHS.get(transform)
            if not isinstance(transform, str) or allowed_paths is None:
                failures.append(
                    f"[manifest] retained entry has unknown projection_transform: {relative}"
                )
            elif relative not in allowed_paths:
                failures.append(
                    f"[manifest] projection_transform is not allowed for: {relative}"
                )
            if entry.get("projection_sha256") is not None:
                failures.append(
                    f"[manifest] retained entry cannot combine projection digest and transform: {relative}"
                )
        result[relative] = entry
    return result


def public_paths(root: Path, failures: list[str]) -> list[str]:
    try:
        lines = (root / DEFAULT_ALLOWLIST).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        failures.append(f"[projection] cannot read public allowlist: {exc}")
        return []
    return [line for line in lines if line and not line.startswith("#")]


def ledger_identity(
    root: Path, relative: Path, decision: str, failures: list[str]
) -> dict | None:
    try:
        payload = json.loads((root / relative).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        failures.append(f"[authority] cannot read {relative.as_posix()}: {exc}")
        return None
    candidate = payload.get("candidate") if isinstance(payload, dict) else None
    disposition = payload.get("disposition") if isinstance(payload, dict) else None
    if (
        not isinstance(candidate, dict)
        or not isinstance(disposition, dict)
        or disposition.get("decision") != decision
    ):
        failures.append(
            f"[authority] {relative.as_posix()} does not record {decision}"
        )
        return None
    return candidate


def check_identity(root: Path, manifest_path: Path) -> list[str]:
    failures: list[str] = []
    manifest = read_json(manifest_path, failures)
    if manifest is None:
        return failures
    if type(manifest.get("schema")) is not int or manifest.get("schema") != 1:
        failures.append("[manifest] schema must be 1")
    former = manifest.get("former")
    if not isinstance(former, dict):
        return ["[manifest] former identity is missing"]
    terms = [
        value.casefold()
        for key in ("display_name", "slug")
        if isinstance((value := former.get(key)), str) and value
    ]
    if not terms:
        failures.append("[manifest] former identity terms are missing")
    current = manifest.get("current")
    if not isinstance(current, dict):
        failures.append("[manifest] current identity is missing")
        current = {}
    accepted_identity = ledger_identity(
        root, ACCEPTED_LEDGER, "accept", failures
    )
    former_identity = ledger_identity(
        root, FORMER_LEDGER, "reject", failures
    )
    identity_keys = ("display_name", "slug")
    if accepted_identity is not None and any(
        current.get(key) != accepted_identity.get(key) for key in identity_keys
    ):
        failures.append(
            "[authority] current identity does not match the accepted ledger"
        )
    if former_identity is not None and any(
        former.get(key) != former_identity.get(key) for key in identity_keys
    ):
        failures.append(
            "[authority] former identity does not match the rejected ledger"
        )
    current_repository = current.get("repository")
    current_display = current.get("display_name")
    current_slug = current.get("slug")
    current_skill = current.get("skill")
    former_slug = former.get("slug")
    retired_on = former.get("retired_on")
    former_repository = None
    if isinstance(current_repository, str) and isinstance(former_slug, str):
        prefix, separator, _ = current_repository.rstrip("/").rpartition("/")
        if separator and prefix:
            former_repository = f"{prefix}/{former_slug}"
    former_skill = None
    if (
        isinstance(current_skill, str)
        and isinstance(current_slug, str)
        and isinstance(former_slug, str)
    ):
        former_skill = current_skill.replace(current_slug, former_slug)
    retained = retained_paths(manifest, failures)
    manifest_rel = manifest_path.relative_to(root).as_posix()
    projection = (root / "PROJECTION-PROVENANCE.md").is_file()
    current_identity_found = False
    for relative in public_paths(root, failures):
        if relative == manifest_rel:
            continue
        classified = relative in retained
        if (
            isinstance(former_slug, str)
            and former_slug.casefold() in relative.casefold()
            and not classified
        ):
            failures.append(
                f"[legacy-path] {relative} retains the former slug"
            )
        if relative == DEFAULT_ALLOWLIST.as_posix():
            continue
        path = root / relative
        if not path.is_file():
            failures.append(
                f"[projection] allowlisted path is missing: {relative}"
            )
            continue
        if classified:
            projection_transform = retained[relative].get("projection_transform")
            transformed_projection = (
                projection
                and projection_transform in PROJECTION_TRANSFORM_PATHS
                and relative in PROJECTION_TRANSFORM_PATHS[projection_transform]
            )
            if not transformed_projection:
                expected_digest = (
                    retained[relative].get("projection_sha256")
                    if projection and retained[relative].get("projection_sha256")
                    else retained[relative].get("sha256")
                )
                actual_digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if expected_digest != actual_digest:
                    failures.append(
                        f"[retained] {relative} bytes do not match the manifest digest"
                    )
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        folded = text.casefold()
        if (
            isinstance(current_display, str)
            and current_display
            and current_display.casefold() in folded
        ):
            current_identity_found = True
            if isinstance(retired_on, str) and not classified:
                for line in text.splitlines():
                    if current_display.casefold() not in line.casefold():
                        continue
                    for date_text in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", line):
                        if date_text < retired_on:
                            failures.append(
                                f"[chronology] {relative} pairs {current_display} "
                                f"with pre-selection date {date_text}"
                            )
        stale_repository = (
            isinstance(former_repository, str)
            and former_repository.casefold() in folded
        )
        stale_skill = (
            isinstance(former_skill, str)
            and former_skill.casefold() in folded
        )
        former_occurrence = (
            any(term in folded for term in terms)
            or stale_repository
            or stale_skill
            or (
                isinstance(former_slug, str)
                and former_slug.casefold() in relative.casefold()
            )
            or (
                projection
                and classified
                and retained[relative].get("projection_transform")
                    == "private_evidence_redaction"
                and PRIVATE_EVIDENCE_REDACTION.casefold() in folded
            )
        )
        if classified and not former_occurrence:
            failures.append(
                f"[retained] {relative} classifies no former-identity occurrence"
            )
        if stale_repository and not classified:
            failures.append(
                f"[current] {relative} contains the former repository coordinate"
            )
        elif stale_skill and not classified:
            failures.append(
                f"[current] {relative} contains the former skill identifier"
            )
        elif any(term in folded for term in terms) and not classified:
            failures.append(
                f"[legacy] {relative} contains an unclassified former-identity match"
            )
    if (
        isinstance(current_display, str)
        and current_display
        and not current_identity_found
    ):
        failures.append(
            f"[current] public files do not identify {current_display}"
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate current and retained identity references."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = (
        args.manifest.resolve()
        if args.manifest
        else root / DEFAULT_MANIFEST
    )
    failures = check_identity(root, manifest)
    if failures:
        for failure in failures:
            print(failure)
        print(f"FAIL: {len(failures)} identity finding(s)")
        return 1
    print("OK: identity checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
