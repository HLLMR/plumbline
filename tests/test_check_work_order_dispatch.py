# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Tests for checks/check_work_order_dispatch.py.

Standard library only. Every fixture is a small, isolated git repository
built from scratch in a temporary directory (or, for the real-tree case, a
filtered copy of this repository) so each defect class is observed firing
rather than assumed. Nothing is written outside the fixture directory.
Assertions run through the checker's public CLI (subprocess), matching the
`Required interface` in WO-PL-014.
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "checks" / "check_work_order_dispatch.py"
ADAPTER = REPO_ROOT / "adapters" / "claude-code" / "wo_capability_wall.py"
ADAPTER_README = REPO_ROOT / "adapters" / "claude-code" / "README.md"
SKIP_DIRS = {".git", "dist", "__pycache__", ".pytest_cache", "bootstrap"}

_spec = importlib.util.spec_from_file_location("_dispatch_check", CHECKER)
dispatch = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dispatch)

_wall_spec = importlib.util.spec_from_file_location("_capability_wall", ADAPTER)
wall = importlib.util.module_from_spec(_wall_spec)
_wall_spec.loader.exec_module(wall)


def run_git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=30)


def git_commit_all(repo: Path, message: str = "fixture") -> None:
    run_git(repo, "init", "-q")
    run_git(repo, "config", "user.email", "fixture@example.invalid")
    run_git(repo, "config", "user.name", "Fixture")
    run_git(repo, "add", "-A")
    run_git(repo, "commit", "-q", "-m", message)


VALID_GRANT = {
    "filesystem.write": ["checks/foo.py", "tests/test_foo.py"],
    "filesystem.read.deny": ["archive/**"],
    "shell.execute": "restricted",
    "network.egress": "denied",
    "package.install": "denied",
    "secrets.read": "denied",
    "git.commit": "denied",
    "git.push": "denied",
}
VALID_EXCEPTIONS = [
    {"path": ".claude/active-wo.txt", "role": "owner_activation_pointer"},
    {"path": "governance/work-orders/**", "role": "owner_issued_work_order_scope"},
]


def render_frontmatter(wo_id="WO-PL-900", status="ACTIVE", doctrine_rev="0.6",
                       grant=None, exceptions=None, extra_top_lines=""):
    grant = VALID_GRANT if grant is None else grant
    exceptions = VALID_EXCEPTIONS if exceptions is None else exceptions
    lines = ["---", f"id: {wo_id}", f"status: {status}", f"doctrine_rev: {doctrine_rev}",
             "repository: this repository, as the session project root"]
    if extra_top_lines:
        lines.append(extra_top_lines)
    lines.append("grant:")
    if "filesystem.write" in grant:
        lines.append("  filesystem.write:")
        for entry in grant["filesystem.write"]:
            lines.append(f"    - {entry}")
    if "filesystem.read.deny" in grant:
        lines.append("  filesystem.read.deny:")
        for entry in grant["filesystem.read.deny"]:
            lines.append(f"    - {entry}")
    for key in dispatch.CAPABILITY_KEYS:
        if key in grant:
            lines.append(f"  {key}: {grant[key]}")
    lines.append("enforced_by:")
    lines.append("unenforced_boundaries:")
    for key in grant:
        lines.append(f"  - {key}")
    if exceptions:
        lines.append("dispatch_validation:")
        lines.append("  prose_path_exceptions:")
        for entry in exceptions:
            lines.append(f"    - path: {entry['path']}")
            lines.append(f"      role: {entry['role']}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def render_body(wo_id="WO-PL-900", grant=None, exceptions=None, extra_b3=""):
    grant = VALID_GRANT if grant is None else grant
    exceptions = VALID_EXCEPTIONS if exceptions is None else exceptions
    normalized = dispatch.validate_grant(dict(grant), dispatch.Failures())
    boundary_lines = dispatch.render_boundary_lines(normalized, exceptions)
    lines = [
        f"# {wo_id}: fixture work order",
        "",
        "## Status",
        "",
        "**ACTIVE.**",
        "",
        "## B.3 Baseline, wall proof, and gates",
        "",
        "Fixture baseline text.",
        extra_b3,
        "",
        dispatch.BEGIN_MARKER,
        *boundary_lines,
        dispatch.END_MARKER,
        "",
        "## Acceptance",
        "",
        "Fixture acceptance text.",
        "",
    ]
    return "\n".join(lines) + "\n"


def make_work_order_text(**kwargs):
    fm_kwargs = {k: v for k, v in kwargs.items()
                if k in ("wo_id", "status", "doctrine_rev", "grant", "exceptions",
                        "extra_top_lines")}
    body_kwargs = {k: v for k, v in kwargs.items()
                  if k in ("wo_id", "grant", "exceptions", "extra_b3")}
    return render_frontmatter(**fm_kwargs) + "\n" + render_body(**body_kwargs)


class DispatchTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        (self.repo / "checks").mkdir()
        shutil.copy(CHECKER, self.repo / "checks" / "check_work_order_dispatch.py")
        (self.repo / "governance" / "work-orders").mkdir(parents=True)
        (self.repo / ".claude").mkdir()
        (self.repo / "DOCTRINE.md").write_text(
            "# Doctrine\n\n| Revision | 0.6 |\n| Status | Ratified |\n",
            encoding="utf-8", newline="\n")

    def write_wo(self, name="WO-PL-900-fixture.md", **kwargs) -> Path:
        path = self.repo / "governance" / "work-orders" / name
        path.write_bytes(make_work_order_text(**kwargs).encode("utf-8"))
        return path

    def set_pointer(self, target: str) -> None:
        (self.repo / ".claude" / "active-wo.txt").write_bytes(
            (target + "\n").encode("utf-8"))

    def commit(self):
        git_commit_all(self.repo)

    def run_checker(self, *args):
        return subprocess.run(
            [sys.executable, str(self.repo / "checks" / "check_work_order_dispatch.py"), *args],
            cwd=self.repo, capture_output=True, text=True, timeout=60)

    def assert_fails(self, result, category):
        self.assertNotEqual(result.returncode, 0, f"expected failure:\n{result.stdout}")
        self.assertIn(f"[{category}]", result.stdout,
                      f"expected a [{category}] failure:\n{result.stdout}")

    def assert_ok(self, result):
        self.assertEqual(result.returncode, 0, f"expected success:\n{result.stdout}\n{result.stderr}")


class RuntimeParserCompatibilityTests(unittest.TestCase):
    def test_runtime_and_dispatch_normalize_the_consumed_fields_identically(self):
        corpus = (
            ("block", render_frontmatter(doctrine_rev="0.8")),
            ("inline", "\n".join((
                "---", "id: WO-PL-900", "status: ACTIVE", "doctrine_rev: 0.8",
                "grant:", "  filesystem.write: [README.md, tests/**]",
                "  filesystem.read.deny: [archive/**]",
                "  shell.execute: denied", "  network.egress: allowed",
                "  package.install: denied", "  secrets.read: denied",
                "  git.commit: denied", "  git.push: denied", "---", "",
            ))),
            ("block-comment-and-unmatched-quote", "\n".join((
                "---", "id: WO-PL-900", "status: ACTIVE", "doctrine_rev: 0.8",
                "grant:", "  filesystem.write:", "    - safe.txt # comment",
                "    - 'literal-leading-quote.txt",
                "  filesystem.read.deny: [archive/**]",
                "  shell.execute: denied", "  network.egress: allowed",
                "  package.install: denied", "  secrets.read: denied",
                "  git.commit: denied", "  git.push: denied", "---", "",
            ))),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            for label, text in corpus:
                with self.subTest(case=label):
                    lines = wall.extract_frontmatter(text)
                    runtime = wall.runtime_contract(lines, root)
                    fields = dispatch.parse_frontmatter(lines)
                    failures = dispatch.Failures()
                    checker = dispatch.runtime_contract(fields, failures)
                    self.assertFalse(failures.items, failures.items)
                    self.assertEqual(runtime, checker)

    def test_runtime_and_dispatch_both_reject_authority_parser_aliases(self):
        corpus = (
            render_frontmatter(doctrine_rev="0.8").replace(
                "  network.egress: denied", "  network.egress: ALLOWED"),
            render_frontmatter(doctrine_rev="0.8").replace(
                "  filesystem.write:\n    - checks/foo.py\n    - tests/test_foo.py",
                "  filesystem.write: 'tests/test_foo.py"),
            render_frontmatter(doctrine_rev="0.8").replace(
                "status: ACTIVE", "status: 'ACTIVE"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            for text in corpus:
                lines = wall.extract_frontmatter(text)
                with self.subTest(text=text):
                    with self.assertRaises(wall.Denied):
                        wall.runtime_contract(lines, root)
                    fields = dispatch.parse_frontmatter(lines)
                    failures = dispatch.Failures()
                    dispatch.runtime_contract(fields, failures)
                    self.assertTrue(failures.items)

    def test_runtime_and_dispatch_recognize_the_same_protected_targets(self):
        text = render_frontmatter(doctrine_rev="0.8")
        relpath = "governance/work-orders/WO-PL-900-fixture.md"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            lines = wall.extract_frontmatter(text)
            runtime = wall.runtime_contract(lines, root, relpath)
            fields = dispatch.parse_frontmatter(lines)
            failures = dispatch.Failures()
            checker = dispatch.runtime_contract(fields, failures, relpath)
        self.assertFalse(failures.items, failures.items)
        self.assertEqual(runtime["protected_control_plane"],
                         checker["protected_control_plane"])
        self.assertEqual(runtime["protected_control_plane"], [
            ".claude/active-wo.txt",
            ".claude/hooks/**",
            ".claude/hooks/wo_capability_wall.py",
            ".claude/settings.json",
            ".claude/settings.local.json",
            "governance/LOG-denials.jsonl",
            relpath,
        ])

    def test_runtime_and_dispatch_both_reject_unsupported_path_grammar(self):
        for entry in ("checks//foo.py", "checks/./foo.py", "checks/foo.py/",
                      "~/foo.py", "checks/foo\x00.py"):
            grant = dict(VALID_GRANT)
            grant["filesystem.write"] = [entry]
            text = render_frontmatter(doctrine_rev="0.8", grant=grant)
            lines = wall.extract_frontmatter(text)
            with tempfile.TemporaryDirectory() as tmp, self.subTest(entry=entry):
                with self.assertRaises(wall.Denied):
                    wall.runtime_contract(lines, Path(tmp).resolve())
                fields = dispatch.parse_frontmatter(lines)
                failures = dispatch.Failures()
                dispatch.runtime_contract(fields, failures)
                self.assertTrue(failures.items)


class AdopterDocumentationWorkOrderTests(DispatchTestCase):
    def test_readme_birth_test_example_passes_the_shipped_validator(self):
        readme = ADAPTER_README.read_text(encoding="utf-8")
        marker = "WO-000 for the test, at `governance/work-orders/WO-000-birth-test.md`:"
        tail = readme.split(marker, 1)[1]
        example = tail.split("```", 2)[1].strip() + "\n"
        (self.repo / "DOCTRINE.md").write_text(
            "# Doctrine\n\n| Revision | 0.8 |\n| Status | Ratified |\n",
            encoding="utf-8", newline="\n")
        path = self.repo / "governance" / "work-orders" / "WO-000-birth-test.md"
        path.write_text(example, encoding="utf-8", newline="\n")
        self.commit()
        result = self.run_checker(
            "--work-order", "governance/work-orders/WO-000-birth-test.md")
        self.assert_ok(result)


# --------------------------------------------------------------------------
# 1-2: lockout
# --------------------------------------------------------------------------

class LockoutTests(DispatchTestCase):
    def test_no_pointer_lockout_succeeds(self):
        self.commit()
        self.assert_ok(self.run_checker("--lockout"))

    def test_lockout_fails_when_pointer_exists(self):
        self.set_pointer("governance/work-orders/does-not-matter.md")
        self.commit()
        self.assert_fails(self.run_checker("--lockout"), "lockout")


# --------------------------------------------------------------------------
# 3: missing .txt with a .tx sibling
# --------------------------------------------------------------------------

class PointerExtensionTests(DispatchTestCase):
    def test_tx_sibling_without_txt_fails_active(self):
        (self.repo / ".claude" / "active-wo.tx").write_text(
            "governance/work-orders/WO-PL-900-fixture.md\n", encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--active"), "pointer")

    def test_tx_sibling_fails_lockout(self):
        (self.repo / ".claude" / "active-wo.tx").write_text(
            "governance/work-orders/WO-PL-900-fixture.md\n", encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--lockout"), "pointer")


# --------------------------------------------------------------------------
# 4: pointer to missing, outside, non-work-order, non-ACTIVE, mismatched-ID
# --------------------------------------------------------------------------

class PointerTargetTests(DispatchTestCase):
    def test_pointer_to_missing_file_fails(self):
        self.set_pointer("governance/work-orders/does-not-exist.md")
        self.commit()
        self.assert_fails(self.run_checker("--active"), "pointer")

    def test_pointer_outside_work_orders_fails(self):
        (self.repo / "README.md").write_text("hello\n", encoding="utf-8", newline="\n")
        self.set_pointer("README.md")
        self.commit()
        self.assert_fails(self.run_checker("--active"), "pointer")

    def test_pointer_to_non_active_status_fails(self):
        self.write_wo(status="COMPLETE")
        self.set_pointer("governance/work-orders/WO-PL-900-fixture.md")
        self.commit()
        self.assert_fails(self.run_checker("--active"), "frontmatter")

    def test_pointer_to_mismatched_id_fails(self):
        self.write_wo(wo_id="WO-PL-901")
        self.set_pointer("governance/work-orders/WO-PL-900-fixture.md")
        self.commit()
        self.assert_fails(self.run_checker("--active"), "frontmatter")

    def test_pointer_with_doubled_slash_rejected_not_normalized(self):
        self.write_wo()
        self.set_pointer("governance//work-orders/WO-PL-900-fixture.md")
        self.commit()
        self.assert_fails(self.run_checker("--active"), "pointer")

    def test_pointer_with_trailing_slash_rejected(self):
        self.write_wo()
        self.set_pointer("governance/work-orders/WO-PL-900-fixture.md/")
        self.commit()
        self.assert_fails(self.run_checker("--active"), "pointer")

    def test_pointer_with_leading_whitespace_rejected_not_trimmed(self):
        self.write_wo()
        self.set_pointer("  governance/work-orders/WO-PL-900-fixture.md")
        self.commit()
        self.assert_fails(self.run_checker("--active"), "pointer")

    def test_pointer_with_trailing_whitespace_rejected_not_trimmed(self):
        self.write_wo()
        self.set_pointer("governance/work-orders/WO-PL-900-fixture.md  ")
        self.commit()
        self.assert_fails(self.run_checker("--active"), "pointer")


# --------------------------------------------------------------------------
# 5: CRLF, BOM, NUL, invalid UTF-8, missing/duplicate frontmatter keys
# --------------------------------------------------------------------------

class ByteAndFrontmatterTests(DispatchTestCase):
    def test_crlf_fails(self):
        path = self.write_wo()
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "bytes")

    def test_bom_fails(self):
        path = self.write_wo()
        path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "bytes")

    def test_nul_byte_fails(self):
        path = self.write_wo()
        path.write_bytes(path.read_bytes() + b"\x00")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "bytes")

    def test_invalid_utf8_fails(self):
        path = self.write_wo()
        path.write_bytes(path.read_bytes() + b"\xff\xfe")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "bytes")

    def test_missing_frontmatter_key_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("doctrine_rev: 0.6\n", "")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "frontmatter")

    def test_duplicate_frontmatter_key_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("id: WO-PL-900\n", "id: WO-PL-900\nid: WO-PL-900\n")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "frontmatter")

    def test_missing_enforced_by_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("enforced_by:\n", "")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "manifest")

    def test_missing_unenforced_boundaries_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        start = text.index("unenforced_boundaries:\n")
        end = text.index("dispatch_validation:\n", start)
        path.write_text(text[:start] + text[end:], encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "manifest")

    def test_active_status_cannot_coexist_with_retirement_metadata(self):
        for metadata in ("void: true", "superseded_by: WO-PL-901",
                         "void : true", "superseded_by : WO-PL-901"):
            with self.subTest(metadata=metadata):
                self.write_wo(extra_top_lines=metadata)
                self.commit()
                result = self.run_checker(
                    "--work-order",
                    "governance/work-orders/WO-PL-900-fixture.md")
                self.assert_fails(result, "frontmatter")


# --------------------------------------------------------------------------
# 6: absent/empty grant, duplicate paths, unsafe path syntax, unsupported values
# --------------------------------------------------------------------------

class GrantTests(DispatchTestCase):
    def test_scalar_grant_fails_without_traceback(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        start = text.index("grant:\n")
        end = text.index("enforced_by:\n", start)
        path.write_text(text[:start] + "grant: denied\n" + text[end:],
                        encoding="utf-8", newline="\n")
        self.commit()
        result = self.run_checker(
            "--work-order", "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "grant")
        self.assertNotIn("Traceback", result.stderr)

    def test_empty_write_grant_fails(self):
        self.write_wo(grant={"filesystem.write": [], **{k: v for k, v in VALID_GRANT.items()
                                                        if k != "filesystem.write"}})
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "grant")

    def test_duplicate_write_path_fails(self):
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = ["checks/foo.py", "checks/foo.py"]
        self.write_wo(grant=grant)
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "grant")

    def test_unsafe_path_syntax_fails(self):
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = ["../escape.py"]
        self.write_wo(grant=grant)
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "grant")

    def test_absolute_path_syntax_fails(self):
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = ["/etc/passwd"]
        self.write_wo(grant=grant)
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "grant")

    def test_unsupported_capability_value_fails(self):
        grant = dict(VALID_GRANT)
        grant["shell.execute"] = "sometimes"
        self.write_wo(grant=grant)
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "grant")

    def test_empty_component_double_slash_rejected_not_normalized(self):
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = ["checks/foo.py", "checks//bar.py"]
        self.write_wo(grant=grant)
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "grant")

    def test_empty_component_trailing_slash_rejected(self):
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = ["checks/foo.py", "checks/"]
        self.write_wo(grant=grant)
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "grant")

    def test_unknown_grant_key_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        self.assertIn("  git.push: denied\n", text)
        text = text.replace("  git.push: denied\n", "  git.push: denied\n  shell.exec: denied\n")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "grant")

    def test_unknown_dispatch_validation_key_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        self.assertIn("dispatch_validation:\n  prose_path_exceptions:", text)
        text = text.replace("dispatch_validation:\n  prose_path_exceptions:",
                            "dispatch_validation:\n  extra_key: nope\n  prose_path_exceptions:")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "grant")

    def test_unknown_exception_entry_key_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        needle = "    - path: .claude/active-wo.txt\n      role: owner_activation_pointer\n"
        self.assertIn(needle, text)
        text = text.replace(needle, needle[:-1] + "\n      extra: nope\n")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"), "grant")


class ManifestClassificationTests(DispatchTestCase):
    def test_optional_read_deny_may_be_omitted_and_unclassified(self):
        grant = {key: value for key, value in VALID_GRANT.items()
                 if key != "filesystem.read.deny"}
        self.write_wo(grant=grant)
        self.commit()
        self.assert_ok(self.run_checker(
            "--work-order", "governance/work-orders/WO-PL-900-fixture.md"))

    def test_unknown_unenforced_surface_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("unenforced_boundaries:\n",
                            "unenforced_boundaries:\n  - imaginary.surface\n")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "manifest")

    def test_duplicate_unenforced_surface_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("unenforced_boundaries:\n",
                            "unenforced_boundaries:\n  - shell.execute\n")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "manifest")

    def test_unclassified_declared_surface_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("  - git.push\n", "")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "manifest")

    def test_surface_classified_as_enforced_and_unenforced_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("enforced_by:\n",
                            "enforced_by:\n  shell.execute: fixture wall\n")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "manifest")

    def test_enforced_by_cannot_classify_undeclared_surface(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("enforced_by:\n",
                            "enforced_by:\n  imaginary.surface: fixture wall\n")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "manifest")

    def test_enforced_surface_requires_a_mechanism(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("enforced_by:\n",
                            "enforced_by:\n  shell.execute:\n")
        text = text.replace("  - shell.execute\n", "")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "manifest")

    def test_enforced_by_wrong_type_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("enforced_by:\n", "enforced_by: [shell.execute]\n")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "manifest")

    def test_unenforced_boundaries_wrong_type_fails(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        start = text.index("unenforced_boundaries:\n")
        end = text.index("dispatch_validation:\n", start)
        path.write_text(text[:start] + "unenforced_boundaries: shell.execute\n" +
                        text[end:], encoding="utf-8", newline="\n")
        self.commit()
        self.assert_fails(self.run_checker("--work-order",
                                           "governance/work-orders/WO-PL-900-fixture.md"),
                          "manifest")

    def test_valid_enforced_surface_classification_passes(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("enforced_by:\n",
                            "enforced_by:\n  shell.execute: fixture wall\n")
        text = text.replace("  - shell.execute\n", "")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_ok(self.run_checker("--work-order",
                                        "governance/work-orders/WO-PL-900-fixture.md"))

    def test_empty_inline_enforced_by_mapping_is_accepted(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("enforced_by:\n", "enforced_by: {}\n")
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        self.assert_ok(self.run_checker("--work-order",
                                        "governance/work-orders/WO-PL-900-fixture.md"))


# --------------------------------------------------------------------------
# Appendix B template: the marker pair itself must survive instantiation
# --------------------------------------------------------------------------

class TemplateMarkerInstructionTests(unittest.TestCase):
    def test_b_template_instructs_replacing_content_between_markers_not_the_markers(self):
        text = (REPO_ROOT / "templates" / "B-work-order.md").read_text(encoding="utf-8")
        self.assertEqual(text.count(dispatch.BEGIN_MARKER), 1,
                         "the template must carry exactly one BEGIN marker")
        self.assertEqual(text.count(dispatch.END_MARKER), 1,
                         "the template must carry exactly one END marker")
        begin_at = text.index(dispatch.BEGIN_MARKER)
        end_at = text.index(dispatch.END_MARKER)
        self.assertGreater(end_at, begin_at,
                           "BEGIN must precede END")
        collapsed = " ".join(text.split())
        self.assertNotIn("including these markers", collapsed,
                         "the placeholder instructs removing the markers "
                         "themselves, contrary to DR-004: only the content "
                         "between them is replaced")

    def test_adopting_preserves_markers_and_names_dispatch_mechanics(self):
        text = (REPO_ROOT / "ADOPTING.md").read_text(encoding="utf-8")
        self.assertIn("replace only the content **between**", text)
        self.assertNotIn("markers included, with its exact output", text)
        self.assertIn("`.claude/active-wo.txt`", text)
        self.assertIn("dispatch_validation:\n  prose_path_exceptions:", text)


# --------------------------------------------------------------------------
# Frontmatter parser: list-scalar inline comment stripping vs. quoting
# --------------------------------------------------------------------------

class ListScalarCommentTests(unittest.TestCase):
    def test_unquoted_comment_stripped_quoted_hash_preserved(self):
        lines = [
            "list_field:",
            "  - bare # comment",
            "  - 'quoted # value'",
            '  - "double # value"',
        ]
        fields = dispatch.parse_frontmatter(lines)
        self.assertEqual(fields["list_field"],
                         ["bare", "quoted # value", "double # value"])


# --------------------------------------------------------------------------
# --work-order / --emit-boundaries public-interface path safety
# --------------------------------------------------------------------------

class WorkOrderArgumentPathTests(DispatchTestCase):
    def test_absolute_path_rejected_even_when_it_resolves_inside_repo(self):
        self.write_wo()
        self.commit()
        absolute = str(self.repo / "governance" / "work-orders" / "WO-PL-900-fixture.md")
        result = self.run_checker("--work-order", absolute)
        self.assert_fails(result, "path")

    def test_absolute_path_rejected_for_emit_boundaries(self):
        self.write_wo()
        self.commit()
        absolute = str(self.repo / "governance" / "work-orders" / "WO-PL-900-fixture.md")
        result = self.run_checker("--emit-boundaries", "--work-order", absolute)
        self.assert_fails(result, "path")

    def test_symlinked_candidate_rejected(self):
        self.write_wo()
        self.commit()
        target = self.repo / "governance" / "work-orders" / "WO-PL-900-fixture.md"
        link = self.repo / "governance" / "work-orders" / "WO-PL-901-link.md"
        try:
            link.symlink_to(target)
        except OSError:
            self.skipTest("symlink creation is not permitted in this environment")
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-901-link.md")
        self.assert_fails(result, "path")


# --------------------------------------------------------------------------
# 7: staged or unexpected dirty state
# --------------------------------------------------------------------------

class DirtyTreeTests(DispatchTestCase):
    def test_staged_change_fails(self):
        self.write_wo()
        self.commit()
        (self.repo / "governance" / "work-orders" / "extra.md").write_text(
            "x\n", encoding="utf-8", newline="\n")
        run_git(self.repo, "add", "-A")
        result = self.run_checker("--work-order", "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "git")

    def test_unexpected_untracked_file_fails(self):
        self.write_wo()
        self.commit()
        (self.repo / "governance" / "work-orders" / "stray.md").write_text(
            "x\n", encoding="utf-8", newline="\n")
        result = self.run_checker("--work-order", "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "dirty-tree")

    def test_allowlisted_untracked_file_passes_dirty_tree(self):
        self.write_wo()
        self.commit()
        (self.repo / "governance" / "work-orders" / "stray.md").write_text(
            "x\n", encoding="utf-8", newline="\n")
        result = self.run_checker("--work-order", "governance/work-orders/WO-PL-900-fixture.md",
                                  "--allow", "governance/work-orders/stray.md")
        self.assertNotIn("[dirty-tree]", result.stdout)

    def test_exact_nested_untracked_file_can_be_allowlisted(self):
        self.write_wo()
        self.commit()
        target = self.repo / "skills" / "example" / "assets" / "checks" / "tool.py"
        target.parent.mkdir(parents=True)
        target.write_text("# tool\n", encoding="utf-8", newline="\n")
        result = self.run_checker(
            "--work-order", "governance/work-orders/WO-PL-900-fixture.md",
            "--allow", "skills/example/assets/checks/tool.py")
        self.assertNotIn("[dirty-tree]", result.stdout)

    def test_exact_nested_allowlist_does_not_conceal_untracked_sibling(self):
        self.write_wo()
        self.commit()
        directory = self.repo / "skills" / "example" / "assets" / "checks"
        directory.mkdir(parents=True)
        (directory / "tool.py").write_text(
            "# tool\n", encoding="utf-8", newline="\n")
        (directory / "ungranted.py").write_text(
            "# unrelated\n", encoding="utf-8", newline="\n")
        result = self.run_checker(
            "--work-order", "governance/work-orders/WO-PL-900-fixture.md",
            "--allow", "skills/example/assets/checks/tool.py")
        self.assert_fails(result, "dirty-tree")
        self.assertIn("skills/example/assets/checks/ungranted.py", result.stdout)


# --------------------------------------------------------------------------
# 8: each cache/bytecode residue class
# --------------------------------------------------------------------------

class ResidueTests(DispatchTestCase):
    def _residue_dir(self, name):
        (self.repo / "checks" / name).mkdir()
        (self.repo / "checks" / name / "x").write_text("x", encoding="utf-8")
        self.commit()
        self.assert_fails(self.run_checker("--lockout"), "residue")

    def test_pycache_residue_fails(self):
        self._residue_dir("__pycache__")

    def test_pytest_cache_residue_fails(self):
        self._residue_dir(".pytest_cache")

    def test_mypy_cache_residue_fails(self):
        self._residue_dir(".mypy_cache")

    def test_ruff_cache_residue_fails(self):
        self._residue_dir(".ruff_cache")

    def test_pyc_residue_fails(self):
        (self.repo / "checks" / "x.pyc").write_bytes(b"x")
        self.commit()
        self.assert_fails(self.run_checker("--lockout"), "residue")

    def test_pyo_residue_fails(self):
        (self.repo / "checks" / "x.pyo").write_bytes(b"x")
        self.commit()
        self.assert_fails(self.run_checker("--lockout"), "residue")


# --------------------------------------------------------------------------
# 9: valid candidate and valid active fixtures
# --------------------------------------------------------------------------

class ValidFixtureTests(DispatchTestCase):
    def test_valid_candidate_passes(self):
        self.write_wo()
        self.commit()
        self.assert_ok(self.run_checker("--work-order",
                                        "governance/work-orders/WO-PL-900-fixture.md"))

    def test_valid_active_passes(self):
        self.write_wo()
        self.set_pointer("governance/work-orders/WO-PL-900-fixture.md")
        self.commit()
        self.assert_ok(self.run_checker("--active"))


# --------------------------------------------------------------------------
# 10: normalized grant output and digest stability
# --------------------------------------------------------------------------

class DigestStabilityTests(DispatchTestCase):
    def test_digest_stable_across_runs(self):
        self.write_wo()
        self.commit()
        first = self.run_checker("--work-order", "governance/work-orders/WO-PL-900-fixture.md")
        second = self.run_checker("--work-order", "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_ok(first)
        self.assert_ok(second)
        self.assertIn("effective grant SHA-256:", first.stdout)
        first_digest = [l for l in first.stdout.splitlines() if "SHA-256" in l][0]
        second_digest = [l for l in second.stdout.splitlines() if "SHA-256" in l][0]
        self.assertEqual(first_digest, second_digest)


# --------------------------------------------------------------------------
# 11: no mode and conflicting modes
# --------------------------------------------------------------------------

class ModeTests(DispatchTestCase):
    def test_no_mode_fails(self):
        self.commit()
        self.assert_fails(self.run_checker(), "mode")

    def test_conflicting_modes_fail(self):
        self.commit()
        self.assert_fails(self.run_checker("--lockout", "--active"), "mode")

    def test_emit_boundaries_without_work_order_fails(self):
        self.commit()
        self.assert_fails(self.run_checker("--emit-boundaries"), "mode")


# --------------------------------------------------------------------------
# 13: path-shaped prose tokens
# --------------------------------------------------------------------------

class ProsePathTests(DispatchTestCase):
    def test_resolved_tokens_do_not_fail(self):
        self.write_wo(extra_b3="See `checks/foo.py` and `archive/**` and "
                               "`.claude/active-wo.txt` and `governance/work-orders/**`.")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assertNotIn("[prose-path]", result.stdout)

    def test_unresolved_token_fails(self):
        self.write_wo(extra_b3="See `scripts/unrelated_tool.py` for details.")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "prose-path")
        self.assertIn("prose_path_out_of_grant", result.stdout)

    def test_dotdot_segment_token_always_blocking_not_skipped(self):
        self.write_wo(extra_b3="See `checks/../secret.py` for details.")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "prose-path")
        self.assertIn("prose_path_out_of_grant", result.stdout)

    def test_dot_segment_token_always_blocking(self):
        self.write_wo(extra_b3="See `checks/./foo.py` for details.")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "prose-path")

    def test_git_ref_range_style_token_is_not_false_flagged(self):
        self.write_wo(extra_b3="`origin/main...HEAD` is 0 behind / 2 ahead.")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assertNotIn("[prose-path]", result.stdout)

    def test_bare_directory_mention_without_recursive_suffix_resolves(self):
        grant = dict(VALID_GRANT)
        grant["filesystem.read.deny"] = ["dist/**"]
        self.write_wo(grant=grant, extra_b3="No cache, bytecode, or unrelated `dist/` residue.")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assertNotIn("[prose-path]", result.stdout)

    def test_real_b4_boundaries_section_after_generated_block_is_still_scanned(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            f"{dispatch.END_MARKER}\n",
            f"{dispatch.END_MARKER}\n\n## B.4 BOUNDARIES\n\n"
            "See `scripts/unrelated_tool.py` for details.\n",
            1)
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "prose-path")
        self.assertIn("prose_path_out_of_grant", result.stdout)


# --------------------------------------------------------------------------
# 15: generic Doctrine work-order identifier and optional project namespace
# --------------------------------------------------------------------------

class IdentifierFormatTests(DispatchTestCase):
    def test_generic_doctrine_id_without_namespace_passes(self):
        self.write_wo(name="WO-900-fixture.md", wo_id="WO-900")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-900-fixture.md")
        self.assert_ok(result)

    def test_neutral_namespaced_id_passes(self):
        self.write_wo(name="WO-ACME-900-fixture.md", wo_id="WO-ACME-900")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-ACME-900-fixture.md")
        self.assert_ok(result)

    def test_lowercase_namespace_still_rejected(self):
        self.write_wo(name="WO-acme-900-fixture.md", wo_id="WO-acme-900")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-acme-900-fixture.md")
        self.assert_fails(result, "frontmatter")

    def test_missing_wo_prefix_still_rejected(self):
        self.write_wo(name="900-fixture.md", wo_id="900")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/900-fixture.md")
        self.assert_fails(result, "frontmatter")

    def test_non_three_digit_number_still_rejected(self):
        self.write_wo(name="WO-90-fixture.md", wo_id="WO-90")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-90-fixture.md")
        self.assert_fails(result, "frontmatter")

    def test_double_hyphen_still_rejected(self):
        self.write_wo(name="WO--900-fixture.md", wo_id="WO--900")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO--900-fixture.md")
        self.assert_fails(result, "frontmatter")

    def test_pl_namespace_still_passes(self):
        self.write_wo()
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_ok(result)

    def test_numeric_prefix_collision_is_a_filename_id_mismatch(self):
        self.write_wo(name="WO-9000.md", wo_id="WO-900")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-9000.md")
        self.assert_fails(result, "frontmatter")


# --------------------------------------------------------------------------
# 14: canonical boundaries rendering and byte-exact comparison
# --------------------------------------------------------------------------

class BoundariesTests(DispatchTestCase):
    def test_emit_boundaries_matches_frontmatter(self):
        self.write_wo()
        self.commit()
        result = self.run_checker("--emit-boundaries", "--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_ok(result)
        normalized = dispatch.validate_grant(dict(VALID_GRANT), dispatch.Failures())
        expected = "\n".join(
            dispatch.render_boundary_lines(normalized, VALID_EXCEPTIONS)) + "\n"
        self.assertEqual(result.stdout, expected)

    def test_one_byte_divergence_fails_boundaries_not_generated(self):
        path = self.write_wo()
        text = path.read_text(encoding="utf-8")
        text = text.replace("### Writable repository paths",
                            "### Writable repository  paths", 1)
        path.write_text(text, encoding="utf-8", newline="\n")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "boundaries")
        self.assertIn("boundaries_not_generated", result.stdout)

    def test_end_to_end_from_actual_b_work_order_template(self):
        template_text = (REPO_ROOT / "templates" / "B-work-order.md").read_text(
            encoding="utf-8")
        fence_start = template_text.index("```markdown\n") + len("```markdown\n")
        fence_end = template_text.index("\n```\n", fence_start)
        block = template_text[fence_start:fence_end]

        filled = (block
            .replace("id: WO-[n]", "id: WO-PL-900")
            .replace("doctrine_rev: [x.y]", "doctrine_rev: 0.7")
            .replace("  filesystem.write: [path, path]",
                    "  filesystem.write:\n    - checks/foo.py\n    - tests/test_foo.py")
            .replace("  filesystem.read.deny: [protected paths, if any]",
                    "  filesystem.read.deny:\n    - archive/**")
            .replace("# WO-[n]: [title]", "# WO-PL-900: fixture work order")
            .replace("[Two to four sentences. Cite plan sections by number. Paste routed excerpts\n"
                    "here if the tooling cannot inject them.]",
                    "Fixture context text.")
            .replace("[The falsifiable goal.]", "Fixture objective text.")
            .replace("[Numbered. Each item verifiable.]", "1. Fixture required work item.")
            .replace("[Restate the grant in prose where it matters, plus any unenforced boundaries\n"
                    "the implementer must honor on instruction alone. Those are the weakest part\n"
                    "of this work order and the report must confirm each was respected.]",
                    "Fixture boundaries prose.")
            .replace("[Exact commands and expected results. What the Reviewer verifies from the\n"
                    "report alone.]", "Fixture acceptance text.")
            .replace("[Sections required in the work report.]", "Fixture report format text.")
        )

        self.assertIn("enforced_by: {}", filled)
        for surface in VALID_GRANT:
            pattern = re.compile(rf"^  - {re.escape(surface)}(?:\s|$)", re.MULTILINE)
            occurrences = pattern.findall(filled)
            self.assertEqual(len(occurrences), 1,
                             f"expected exactly one classification of {surface!r}")

        (self.repo / "DOCTRINE.md").write_text(
            "# Doctrine\n\n| Revision | 0.7 |\n| Status | Ratified |\n",
            encoding="utf-8", newline="\n")

        path = self.repo / "governance" / "work-orders" / "WO-PL-900-fixture.md"
        path.write_text(filled, encoding="utf-8", newline="\n")

        emit = self.run_checker("--emit-boundaries", "--work-order",
                                "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_ok(emit)

        begin_at = filled.index(dispatch.BEGIN_MARKER)
        end_at = filled.index(dispatch.END_MARKER) + len(dispatch.END_MARKER)
        generated = (filled[:begin_at] + dispatch.BEGIN_MARKER + "\n" + emit.stdout
                    + dispatch.END_MARKER + filled[end_at:])
        path.write_text(generated, encoding="utf-8", newline="\n")
        self.commit()

        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_ok(result)


# --------------------------------------------------------------------------
# 12: real-tree lockout success through the public CLI
# --------------------------------------------------------------------------

class ControlPlaneSchemaTests(DispatchTestCase):
    """WO-PL-023 phase 2, Doctrine 8.7.4.1-8.7.4.3 and DC.4 compatibility."""

    def make_repo_doctrine(self, revision: str) -> None:
        (self.repo / "DOCTRINE.md").write_text(
            f"# Doctrine\n\n| Revision | {revision} |\n| Status | Ratified |\n",
            encoding="utf-8", newline="\n")

    def write_control_plane_wo(self, *, doctrine_rev: str, grant: dict,
                               extra_top_lines: str = "",
                               name: str = "WO-PL-900-fixture.md") -> Path:
        exceptions = VALID_EXCEPTIONS
        fm = render_frontmatter(doctrine_rev=doctrine_rev, grant=grant,
                                exceptions=exceptions, extra_top_lines=extra_top_lines)
        heading = dispatch.boundaries_heading_for_revision(doctrine_rev)
        probes = None
        if extra_top_lines and "control_plane_probes" in extra_top_lines:
            import re as _re
            probes = [{"path": m.group(1), "role": m.group(2)}
                     for m in _re.finditer(r"path:\s*(\S+)\s*\n\s*role:\s*(\S+)",
                                          extra_top_lines)]
        normalized = dispatch.validate_grant(dict(grant), dispatch.Failures())
        boundary_lines = dispatch.render_boundary_lines(normalized, exceptions, probes, heading)
        body = "\n".join([
            "# WO-PL-900: fixture work order", "", "## Status", "", "**ACTIVE.**", "",
            "## B.3 Baseline, wall proof, and gates", "", "Fixture baseline text.", "",
            dispatch.BEGIN_MARKER, *boundary_lines, dispatch.END_MARKER, "",
            "## Acceptance", "", "Fixture acceptance text.", "",
        ]) + "\n"
        path = self.repo / "governance" / "work-orders" / name
        path.write_bytes((fm + "\n" + body).encode("utf-8"))
        return path

    def test_legacy_0_6_candidate_keeps_b4_heading_and_ignores_control_plane_schema(self):
        """DC.4 compatibility lock: a 0.6-bound candidate is unaffected."""
        self.make_repo_doctrine("0.6")
        grant = dict(VALID_GRANT)
        self.write_control_plane_wo(doctrine_rev="0.6", grant=grant)
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_ok(result)
        emit = self.run_checker("--emit-boundaries", "--work-order",
                                "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_ok(emit)
        self.assertIn("## B.4 Generated boundaries", emit.stdout)
        self.assertNotIn("## B.7", emit.stdout)
        self.assertNotIn("Control-plane falsification probes", emit.stdout)

    def test_legacy_0_7_candidate_with_pointer_in_grant_is_not_rejected(self):
        """DC.4 compatibility: 0.7 never had 8.7, so this is not a new failure."""
        self.make_repo_doctrine("0.7")
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = [".claude/active-wo.txt", "tests/test_foo.py"]
        self.write_control_plane_wo(doctrine_rev="0.7", grant=grant)
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_ok(result)

    def test_0_8_ordinary_candidate_covering_pointer_fails_control_plane(self):
        """Doctrine 8.7.2/8.7.4.1: an ordinary 0.8 candidate may never claim
        mutation authority over a control-plane artifact."""
        self.make_repo_doctrine("0.8")
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = [".claude/active-wo.txt", "tests/test_foo.py"]
        self.write_control_plane_wo(doctrine_rev="0.8", grant=grant)
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "control-plane")
        self.assertIn(".claude/active-wo.txt", result.stdout)

    def test_0_8_ordinary_candidate_cannot_cover_alternate_settings_or_hooks(self):
        self.make_repo_doctrine("0.8")
        for target in (".claude/settings.local.json", ".claude/hooks/disable-wall.py"):
            with self.subTest(target=target):
                grant = dict(VALID_GRANT)
                grant["filesystem.write"] = [target, "tests/test_foo.py"]
                self.write_control_plane_wo(doctrine_rev="0.8", grant=grant)
                self.commit()
                result = self.run_checker(
                    "--work-order", "governance/work-orders/WO-PL-900-fixture.md")
                self.assert_fails(result, "control-plane")

    def test_0_8_birth_test_instrument_with_labeled_exact_probe_passes(self):
        """Doctrine 8.7.4.2: instrument_kind + exact control_plane_probes."""
        self.make_repo_doctrine("0.8")
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = [".claude/active-wo.txt", "tests/test_foo.py"]
        extra = ("instrument_kind: birth-test\n"
                "control_plane_probes:\n"
                "  - path: .claude/active-wo.txt\n"
                "    role: control_plane_falsification_probe")
        self.write_control_plane_wo(doctrine_rev="0.8", grant=grant, extra_top_lines=extra)
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_ok(result)
        emit = self.run_checker("--emit-boundaries", "--work-order",
                                "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_ok(emit)
        self.assertIn("## B.7 Generated boundaries", emit.stdout)
        self.assertIn("Control-plane falsification probes (expected-denial", emit.stdout)
        self.assertIn("confers no authority", emit.stdout)
        self.assertIn(".claude/active-wo.txt", emit.stdout)

    def test_0_8_birth_test_labeled_exact_hook_probe_passes(self):
        """An exact hook-file probe is not an unlabeled hooks-subtree grant."""
        self.make_repo_doctrine("0.8")
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = [
            ".claude/hooks/wo_capability_wall.py",
            "tests/test_foo.py",
        ]
        extra = ("instrument_kind: birth-test\n"
                "control_plane_probes:\n"
                "  - path: .claude/hooks/wo_capability_wall.py\n"
                "    role: control_plane_falsification_probe")
        self.write_control_plane_wo(doctrine_rev="0.8", grant=grant,
                                    extra_top_lines=extra)
        self.commit()
        result = self.run_checker(
            "--work-order", "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_ok(result)

    def test_0_8_probe_role_typo_fails(self):
        self.make_repo_doctrine("0.8")
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = [".claude/active-wo.txt", "tests/test_foo.py"]
        extra = ("instrument_kind: birth-test\n"
                "control_plane_probes:\n"
                "  - path: .claude/active-wo.txt\n"
                "    role: wrong_role")
        self.write_control_plane_wo(doctrine_rev="0.8", grant=grant, extra_top_lines=extra)
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "control-plane")

    def test_0_8_wildcard_probe_path_fails(self):
        self.make_repo_doctrine("0.8")
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = ["governance/work-orders/**", "tests/test_foo.py"]
        extra = ("instrument_kind: birth-test\n"
                "control_plane_probes:\n"
                "  - path: governance/work-orders/**\n"
                "    role: control_plane_falsification_probe")
        self.write_control_plane_wo(doctrine_rev="0.8", grant=grant, extra_top_lines=extra)
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "control-plane")

    def test_0_8_probe_not_matching_any_grant_target_fails(self):
        self.make_repo_doctrine("0.8")
        grant = dict(VALID_GRANT)  # does not include .claude/active-wo.txt
        extra = ("instrument_kind: birth-test\n"
                "control_plane_probes:\n"
                "  - path: .claude/active-wo.txt\n"
                "    role: control_plane_falsification_probe")
        self.write_control_plane_wo(doctrine_rev="0.8", grant=grant, extra_top_lines=extra)
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "control-plane")

    def test_0_8_unlabeled_control_plane_path_on_birth_test_instrument_fails(self):
        """Every control-plane path in the grant must be labeled; none left over."""
        self.make_repo_doctrine("0.8")
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = [".claude/active-wo.txt",
                                     "governance/LOG-denials.jsonl", "tests/test_foo.py"]
        extra = ("instrument_kind: birth-test\n"
                "control_plane_probes:\n"
                "  - path: .claude/active-wo.txt\n"
                "    role: control_plane_falsification_probe")
        self.write_control_plane_wo(doctrine_rev="0.8", grant=grant, extra_top_lines=extra)
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "control-plane")
        self.assertIn("governance/LOG-denials.jsonl", result.stdout)

    def test_0_8_control_plane_probes_without_instrument_kind_fails(self):
        self.make_repo_doctrine("0.8")
        grant = dict(VALID_GRANT)
        grant["filesystem.write"] = [".claude/active-wo.txt", "tests/test_foo.py"]
        extra = ("control_plane_probes:\n"
                "  - path: .claude/active-wo.txt\n"
                "    role: control_plane_falsification_probe")
        self.write_control_plane_wo(doctrine_rev="0.8", grant=grant, extra_top_lines=extra)
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "control-plane")

    def test_0_8_unrecognized_instrument_kind_fails(self):
        self.make_repo_doctrine("0.8")
        grant = dict(VALID_GRANT)
        self.write_control_plane_wo(doctrine_rev="0.8", grant=grant,
                                    extra_top_lines="instrument_kind: something-else")
        self.commit()
        result = self.run_checker("--work-order",
                                  "governance/work-orders/WO-PL-900-fixture.md")
        self.assert_fails(result, "control-plane")


class RealTreeLockoutTest(unittest.TestCase):
    def test_real_tree_copy_passes_lockout_once_pointer_removed(self):
        tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        repo = tmp / "writwall"
        shutil.copytree(REPO_ROOT, repo, ignore=shutil.ignore_patterns(*SKIP_DIRS),
                        dirs_exist_ok=True)
        pointer = repo / ".claude" / "active-wo.txt"
        pointer.unlink(missing_ok=True)
        git_commit_all(repo)
        result = subprocess.run(
            [sys.executable, str(repo / "checks" / "check_work_order_dispatch.py"), "--lockout"],
            cwd=repo, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, f"expected success:\n{result.stdout}\n{result.stderr}")


class RealWorkOrderBoundariesTest(unittest.TestCase):
    """The checker must reproduce WO-PL-014's own seeded B.4 block."""

    def test_emit_boundaries_matches_wo_pl_014_seed(self):
        wo_path = (REPO_ROOT / "governance" / "work-orders" /
                  "WO-PL-014-deterministic-pre-dispatch-validator.md")
        if not wo_path.is_file():
            self.skipTest("WO-PL-014 has been closed and moved out of governance/work-orders/")
        text = wo_path.read_text(encoding="utf-8")
        seeded = dispatch.extract_generated_block(text)
        self.assertIsNotNone(seeded, "WO-PL-014 has no BEGIN/END GENERATED BOUNDARIES markers")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--emit-boundaries", "--work-order",
             "governance/work-orders/WO-PL-014-deterministic-pre-dispatch-validator.md"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, f"emit-boundaries failed:\n{result.stdout}")
        rendered_lines = result.stdout.splitlines()
        self.assertEqual(rendered_lines, seeded,
                         "checker output does not byte-match WO-PL-014's own seeded B.4 block")


class AdopterInstalledCheckerWithoutRootDoctrineTests(unittest.TestCase):
    """The installed checker must work without the methodology source file."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "adopter-repo"
        self.repo.mkdir()
        (self.repo / "checks").mkdir()
        shutil.copy(CHECKER, self.repo / "checks" / "check_work_order_dispatch.py")
        (self.repo / "governance" / "work-orders").mkdir(parents=True)
        (self.repo / ".claude").mkdir()

    def test_valid_candidate_passes_with_no_root_doctrine_md(self):
        path = self.repo / "governance" / "work-orders" / "WO-900-fixture.md"
        path.write_bytes(make_work_order_text(wo_id="WO-900").encode("utf-8"))
        git_commit_all(self.repo)
        result = subprocess.run(
            [sys.executable, str(self.repo / "checks" / "check_work_order_dispatch.py"),
             "--work-order", "governance/work-orders/WO-900-fixture.md"],
            cwd=self.repo, capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0,
                         f"expected success:\n{result.stdout}\n{result.stderr}")


class ProjectBindingIndependentOfMethodologyRevisionTests(DispatchTestCase):
    """A project's bound revision is independent of methodology-source bytes."""

    def test_work_order_pinned_to_0_6_passes_alongside_methodology_doctrine_at_0_7(self):
        (self.repo / "DOCTRINE.md").write_text(
            "# Doctrine\n\n| Revision | 0.7 |\n| Status | Ratified |\n",
            encoding="utf-8", newline="\n")
        self.write_wo()
        self.commit()
        self.assert_ok(self.run_checker("--work-order",
                                        "governance/work-orders/WO-PL-900-fixture.md"))


if __name__ == "__main__":
    unittest.main()
