# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Manage Writwall's repository-external, project-specific privacy screen."""

from __future__ import annotations

import argparse
import contextlib
import getpass
import hashlib
import os
import re
import stat
import sys
import time
import uuid
from collections.abc import Mapping, Sequence
from pathlib import Path


PROFILE_NAME = "private-patterns.txt"
HEADER = (
    "# Writwall local public-projection privacy screen.\n"
    "# One exact private identifier per line. Never add credentials, passwords,\n"
    "# tokens, private keys, recovery codes, or secret record values.\n"
)
CREDENTIAL_SHAPE = re.compile(
    r"(?i)^(?:password|passwd|passphrase|token|api[-_ ]?key|secret|"
    r"private[-_ ]?key|recovery[-_ ]?code|authorization|bearer)\s*[:=]|"
    r"^-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----$"
)


class PrivacyScreenError(RuntimeError):
    """A safe failure whose message contains no profile location or values."""


def canonical_project_root(project_root: Path) -> Path:
    try:
        root = project_root.expanduser().resolve(strict=True)
    except OSError as exc:
        raise PrivacyScreenError("project root is unavailable") from exc
    if not root.is_dir():
        raise PrivacyScreenError("project root is not a directory")
    return root


def project_id(project_root: Path, *, platform: str | None = None) -> str:
    root = canonical_project_root(project_root)
    identity = str(root)
    if (platform or sys.platform).startswith("win"):
        identity = identity.casefold()
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]


def state_root(*, platform: str | None = None,
               environment: Mapping[str, str] | None = None,
               home: Path | None = None) -> Path:
    env = os.environ if environment is None else environment
    override = env.get("WRITWALL_STATE_HOME")
    if override:
        return Path(override).expanduser()
    active_platform = platform or sys.platform
    if active_platform.startswith("win"):
        local = env.get("LOCALAPPDATA")
        if not local:
            raise PrivacyScreenError("local application-data storage is unavailable")
        return Path(local) / "Writwall"
    xdg = env.get("XDG_STATE_HOME")
    if xdg:
        return Path(xdg) / "writwall"
    return (home or Path.home()) / ".local" / "state" / "writwall"


def profile_path(project_root: Path, *, platform: str | None = None,
                 environment: Mapping[str, str] | None = None,
                 home: Path | None = None) -> Path:
    project = canonical_project_root(project_root)
    base = state_root(platform=platform, environment=environment, home=home).resolve()
    path = (base
            / "projects" / project_id(project, platform=platform)
            / PROFILE_NAME)
    if path == project or project in path.parents:
        raise PrivacyScreenError("privacy-screen storage must be outside the project")
    return path


def _profile_is_linklike(path: Path) -> bool:
    try:
        if path.is_symlink():
            return True
        isjunction = getattr(os.path, "isjunction", None)
        return bool(isjunction and isjunction(path))
    except OSError:
        return True


def _assert_managed_components(path: Path) -> None:
    projects = path.parents[1]
    identity = path.parent
    for component, expected_directory in (
        (projects, True), (identity, True), (path, False)
    ):
        if not os.path.lexists(component):
            continue
        if _profile_is_linklike(component):
            raise PrivacyScreenError(
                "privacy-screen storage contains a link or reparse entry"
            )
        if expected_directory and not component.is_dir():
            raise PrivacyScreenError("privacy-screen storage is not a directory")
        if not expected_directory and not component.is_file():
            raise PrivacyScreenError("privacy screen is not a regular local file")


@contextlib.contextmanager
def _locked_profile(path: Path):
    _assert_managed_components(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _assert_managed_components(path)
    lock_path = path.with_name("private-patterns.lock")
    if os.path.lexists(lock_path) and _profile_is_linklike(lock_path):
        raise PrivacyScreenError("privacy-screen lock is not a regular local file")
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise PrivacyScreenError("privacy-screen lock is unavailable") from exc
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise PrivacyScreenError("privacy-screen lock is not a regular local file")
        if os.name == "nt":
            import msvcrt

            if os.fstat(descriptor).st_size == 0:
                os.write(descriptor, b"\0")
                os.fsync(descriptor)
            os.lseek(descriptor, 0, os.SEEK_SET)
            deadline = time.monotonic() + 30
            while True:
                try:
                    msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise PrivacyScreenError("privacy-screen lock timed out") from None
                    time.sleep(0.05)
        else:
            import fcntl

            fcntl.flock(descriptor, fcntl.LOCK_EX)
        _assert_managed_components(path)
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt

                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(descriptor, fcntl.LOCK_UN)
        except OSError:
            pass
        os.close(descriptor)


_WINDOWS_REPLACE_CONTENTION_WINERRORS = frozenset({5, 32, 33})
_WINDOWS_REPLACE_RETRY_DEADLINE_SECONDS = 2.0
_WINDOWS_REPLACE_RETRY_INTERVAL_SECONDS = 0.05


def _replace_with_windows_contention_retry(temporary: Path, path: Path) -> None:
    if sys.platform != "win32":
        os.replace(temporary, path)
        return
    deadline = time.monotonic() + _WINDOWS_REPLACE_RETRY_DEADLINE_SECONDS
    while True:
        try:
            os.replace(temporary, path)
            return
        except OSError as exc:
            if getattr(exc, "winerror", None) not in _WINDOWS_REPLACE_CONTENTION_WINERRORS:
                raise
            if time.monotonic() >= deadline:
                raise
            time.sleep(_WINDOWS_REPLACE_RETRY_INTERVAL_SECONDS)


def _write_patterns(path: Path, patterns: list[str]) -> None:
    _assert_managed_components(path)
    temporary = path.with_name(f".{PROFILE_NAME}.{uuid.uuid4().hex}.tmp")
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(HEADER)
            stream.writelines(f"{value}\n" for value in patterns)
            stream.flush()
            os.fsync(stream.fileno())
        if os.name != "nt":
            temporary.chmod(0o600)
        _replace_with_windows_contention_retry(temporary, path)
    except OSError as exc:
        raise PrivacyScreenError("privacy screen could not be written") from exc
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass


def automatic_patterns(project_root: Path) -> list[str]:
    root = canonical_project_root(project_root)
    candidates = (str(root), root.as_posix())
    seen: set[str] = set()
    patterns: list[str] = []
    for candidate in candidates:
        folded = candidate.casefold()
        if candidate and folded not in seen:
            seen.add(folded)
            patterns.append(candidate)
    return patterns


def read_patterns(path: Path) -> list[str]:
    if _profile_is_linklike(path) or not path.is_file():
        raise PrivacyScreenError("privacy screen is unavailable or invalid")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise PrivacyScreenError("privacy screen is unavailable or invalid") from exc
    return [line.strip() for line in lines
            if line.strip() and not line.lstrip().startswith("#")]


def initialize(project_root: Path) -> int:
    path = profile_path(project_root)
    with _locked_profile(path):
        existing = read_patterns(path) if path.exists() else []
        merged = list(existing)
        folded = {value.casefold() for value in merged}
        for value in automatic_patterns(project_root):
            if value.casefold() not in folded:
                folded.add(value.casefold())
                merged.append(value)
        _write_patterns(path, merged)
        return len(merged)


def add_identifier(project_root: Path, identifier: str) -> int:
    value = identifier.strip()
    if (not value or "\n" in value or "\r" in value or value.startswith("#")):
        raise PrivacyScreenError("private identifier must be one non-comment line")
    if CREDENTIAL_SHAPE.search(value):
        raise PrivacyScreenError(
            "credential-shaped input is not valid privacy-screen data"
        )
    path = profile_path(project_root)
    initialize(project_root)
    with _locked_profile(path):
        patterns = read_patterns(path)
        if value.casefold() not in {pattern.casefold() for pattern in patterns}:
            patterns.append(value)
        _write_patterns(path, patterns)
        return len(patterns)


def status(project_root: Path) -> int:
    path = profile_path(project_root)
    if not path.is_file():
        raise PrivacyScreenError(
            "privacy screen is missing; run 'writwall privacy init --project-root <project>'"
        )
    patterns = read_patterns(path)
    if not patterns:
        raise PrivacyScreenError(
            "privacy screen is empty; run 'writwall privacy init --project-root <project>'"
        )
    return len(patterns)


def resolve_pattern_file(project_root: Path, explicit: Path | None = None) -> Path:
    path = explicit if explicit is not None else profile_path(project_root)
    if not path.is_file():
        raise PrivacyScreenError(
            "privacy screen is missing; run 'writwall privacy init --project-root <project>'"
        )
    if not read_patterns(path):
        raise PrivacyScreenError(
            "privacy screen is empty; run 'writwall privacy init --project-root <project>'"
        )
    return path


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="writwall privacy")
    commands = parser.add_subparsers(dest="privacy_command", required=True)
    for name in ("init", "status"):
        command = commands.add_parser(name)
        command.add_argument("--project-root", required=True, type=Path)
    add = commands.add_parser("add")
    add.add_argument("--project-root", required=True, type=Path)
    add.add_argument("--identifier-stdin", action="store_true")
    add.add_argument("--confirm-no-secrets", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.privacy_command == "init":
            count = initialize(args.project_root)
        elif args.privacy_command == "add":
            if not args.confirm_no_secrets:
                raise PrivacyScreenError(
                    "adding an identifier requires --confirm-no-secrets"
                )
            identifier = (sys.stdin.readline().rstrip("\r\n")
                          if args.identifier_stdin
                          else getpass.getpass("Private identifier (input hidden): "))
            count = add_identifier(args.project_root, identifier)
        else:
            count = status(args.project_root)
    except PrivacyScreenError as exc:
        print(f"privacy screen: stopped ({exc})", file=sys.stderr)
        return 1
    print(f"privacy screen: ready ({count} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
