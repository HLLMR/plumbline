# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the Claude Code capability-wall adapter (Doctrine 8.3.5).

Standard library only. Every test writes exclusively inside its own temporary
fixture directory.
"""
from __future__ import annotations

import importlib.util
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = REPO_ROOT / "adapters" / "claude-code" / "wo_capability_wall.py"
LOG_NAME = "LOG-denials.jsonl"


def outside_repo_target(fixture_root):
    """A platform-native absolute path provably outside a fixture repository.

    Derived from the fixture's own root so it is native to the executing
    platform's path model (drive-letter or POSIX) rather than a foreign OS
    literal.
    """
    sibling = fixture_root.parent / (fixture_root.name + "-outside-target")
    return str(sibling / "outside.ini")


def load_adapter():
    spec = importlib.util.spec_from_file_location("wo_capability_wall", ADAPTER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


wall = load_adapter()


WO_BODY = "# WO-000: fixture\n"


def frontmatter(filesystem_write=("governance/scratch/**",), shell="denied",
                include_grant=True, include_fs=True, include_shell=True,
                read_deny=None, status="ACTIVE", network="denied"):
    lines = ["---", "id: WO-000", f"status: {status}", "doctrine_rev: 0.8"]
    if include_grant:
        lines.append("grant:")
        if include_fs:
            lines.append("  filesystem.write:")
            for entry in filesystem_write:
                lines.append(f"    - {entry}")
        if read_deny is not None:
            lines.append("  filesystem.read.deny:")
            for entry in read_deny:
                lines.append(f"    - {entry}")
        if include_shell:
            lines.append(f"  shell.execute: {shell}")
        lines.append(f"  network.egress: {network}")
    else:
        lines.append("id: WO-000")
    lines.append("---")
    return "\n".join(lines) + "\n" + WO_BODY


class FixtureRepo:
    """A temporary repository with a pointer and a work order."""

    def __init__(self, stack, pointer="governance/work-orders/WO-000.md",
                 wo_text=None, write_pointer=True, write_wo=True):
        self.root = Path(stack.enter_context(tempfile.TemporaryDirectory())).resolve()
        (self.root / ".claude").mkdir(parents=True)
        (self.root / "governance" / "work-orders").mkdir(parents=True)
        (self.root / "governance" / "scratch").mkdir(parents=True)
        if write_pointer:
            (self.root / ".claude" / "active-wo.txt").write_text(pointer, encoding="utf-8")
        if write_wo:
            text = frontmatter() if wo_text is None else wo_text
            target = self.root / "governance" / "work-orders" / "WO-000.md"
            target.write_text(text, encoding="utf-8")


def event(tool, **tool_input):
    return {"tool_name": tool, "tool_input": dict(tool_input)}


class ClassificationTests(unittest.TestCase):
    def test_file_edit_tools_classified(self):
        for tool in ("Edit", "Write", "NotebookEdit", "MultiEdit"):
            self.assertEqual(wall.classify_tool(tool), wall.FILE_EDIT, tool)

    def test_shell_tools_classified(self):
        for tool in ("Bash", "PowerShell", "Monitor", "KillShell"):
            self.assertEqual(wall.classify_tool(tool), wall.SHELL, tool)

    def test_nonmutating_tools_pass_through(self):
        for tool in ("Skill", "TodoWrite"):
            self.assertEqual(wall.classify_tool(tool), wall.NONMUTATING, tool)

    def test_network_tools_require_explicit_supported_egress_authority(self):
        import contextlib
        self.assertEqual(
            {wall.classify_tool(tool) for tool in ("WebSearch", "WebFetch")},
            {wall.NETWORK},
        )
        with contextlib.ExitStack() as stack:
            denied = FixtureRepo(stack, wo_text=frontmatter(network="denied"))
            allowed = FixtureRepo(stack, wo_text=frontmatter(network="allowed"))
            missing = FixtureRepo(
                stack,
                wo_text=frontmatter().replace("  network.egress: denied\n", ""),
            )
            invalid = FixtureRepo(stack, wo_text=frontmatter(network="sometimes"))
            for tool in ("WebSearch", "WebFetch"):
                with self.subTest(tool=tool, mode="denied"):
                    self.assertEqual(
                        wall.decide(event(tool, query="fixture"), denied.root).code,
                        "network_egress_denied",
                    )
                with self.subTest(tool=tool, mode="allowed"):
                    self.assertIsNone(
                        wall.decide(event(tool, query="fixture"), allowed.root))
                with self.subTest(tool=tool, mode="missing"):
                    self.assertEqual(
                        wall.decide(event(tool, query="fixture"), missing.root).code,
                        "network_egress_invalid",
                    )
                with self.subTest(tool=tool, mode="invalid"):
                    self.assertEqual(
                        wall.decide(event(tool, query="fixture"), invalid.root).code,
                        "network_egress_invalid",
                    )

    def test_read_tools_classified(self):
        for tool in ("Read", "Glob", "Grep", "LS", "NotebookRead"):
            self.assertEqual(wall.classify_tool(tool), wall.FILE_READ, tool)

    def test_every_known_unsupported_mutation_tool_denies(self):
        for tool in sorted(wall.UNSUPPORTED_MUTATION_TOOLS):
            with self.subTest(tool=tool):
                self.assertEqual(wall.classify_tool(tool), wall.UNSUPPORTED)

    def test_unknown_tool_denies(self):
        for tool in ("SomeFutureTool", "", None, 42):
            with self.subTest(tool=tool):
                self.assertEqual(wall.classify_tool(tool), wall.UNSUPPORTED)

    def test_every_mcp_tool_denies_by_default(self):
        self.assertEqual(wall.classify_tool("mcp__notion__create"), wall.UNSUPPORTED)
        self.assertEqual(wall.classify_tool("mcp__anything"), wall.UNSUPPORTED)

    def test_opaque_mcp_resource_readers_are_not_called_nonmutating(self):
        for tool in ("ReadMcpResourceTool", "ReadMcpResourceDirTool"):
            with self.subTest(tool=tool):
                self.assertEqual(wall.classify_tool(tool), wall.UNSUPPORTED)

    def test_categories_are_disjoint(self):
        sets = [wall.FILE_EDIT_TOOLS, wall.READ_TOOLS, wall.SHELL_TOOLS,
                wall.NETWORK_TOOLS, wall.NONMUTATING_TOOLS,
                wall.UNSUPPORTED_MUTATION_TOOLS]
        for i, left in enumerate(sets):
            for right in sets[i + 1:]:
                self.assertEqual(left & right, frozenset())


class UnsupportedToolDenialTests(unittest.TestCase):
    def setUp(self):
        import contextlib
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)

    def test_unsupported_tools_deny_even_with_valid_wo(self):
        repo = FixtureRepo(self.stack)
        for tool in sorted(wall.UNSUPPORTED_MUTATION_TOOLS) + [
                "mcp__x__y", "BrandNewTool", "ReadMcpResourceTool",
                "ReadMcpResourceDirTool"]:
            with self.subTest(tool=tool):
                reason = wall.decide(event(tool), repo.root)
                self.assertIsNotNone(reason)
                self.assertIn("not modeled", reason)
                self.assertIn("RFI", reason)

    def test_nonmutating_allowed_with_no_work_order(self):
        repo = FixtureRepo(self.stack, write_pointer=False)
        self.assertIsNone(wall.decide(event("Read", file_path="anything"), repo.root))


class PointerTests(unittest.TestCase):
    def setUp(self):
        import contextlib
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)

    def deny_reason(self, **kwargs):
        repo = FixtureRepo(self.stack, **kwargs)
        return wall.decide(event("Write", file_path="governance/scratch/a.txt"), repo.root)

    def test_no_pointer_denies(self):
        reason = self.deny_reason(write_pointer=False)
        self.assertIn("No active work order", reason)

    def test_empty_pointer_denies(self):
        self.assertIn("empty", self.deny_reason(pointer="   \n"))

    def test_dangling_pointer_denies(self):
        reason = self.deny_reason(pointer="governance/work-orders/MISSING.md", write_wo=False)
        self.assertIn("missing file", reason)

    def test_absolute_pointer_denies(self):
        self.assertIn("not repository-relative",
                      self.deny_reason(pointer="C:/evil/WO.md"))
        self.assertIn("not repository-relative",
                      self.deny_reason(pointer="/etc/WO.md"))

    def test_parent_escape_pointer_denies(self):
        self.assertIn("escapes the repository",
                      self.deny_reason(pointer="governance/work-orders/../../../WO.md"))

    def test_pointer_outside_work_orders_denies(self):
        self.assertIn("resolves outside",
                      self.deny_reason(pointer="bootstrap/WO.md"))

    def test_non_markdown_pointer_denies(self):
        self.assertIn("Markdown",
                      self.deny_reason(pointer="governance/work-orders/WO.txt"))

    def test_directory_pointer_denies(self):
        repo = FixtureRepo(self.stack, pointer="governance/work-orders/adir.md")
        (repo.root / "governance" / "work-orders" / "adir.md").mkdir()
        reason = wall.decide(event("Write", file_path="governance/scratch/a.txt"), repo.root)
        self.assertIn("directory", reason)

    def test_backslash_pointer_denies(self):
        self.assertIn("backslash",
                      self.deny_reason(pointer="governance\\work-orders\\WO-000.md"))


class FrontmatterTests(unittest.TestCase):
    def setUp(self):
        import contextlib
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)

    def reason_for(self, wo_text, tool="Write", **tool_input):
        repo = FixtureRepo(self.stack, wo_text=wo_text)
        if not tool_input:
            tool_input = {"file_path": "governance/scratch/a.txt"}
        return wall.decide(event(tool, **tool_input), repo.root)

    def test_missing_opening_fence_denies(self):
        reason = self.reason_for("grant:\n  shell.execute: allowed\n---\n")
        self.assertIn("frontmatter fence", reason)

    def test_missing_closing_fence_denies(self):
        reason = self.reason_for("---\ngrant:\n  shell.execute: allowed\n")
        self.assertIn("no closing", reason)

    def test_missing_grant_denies(self):
        reason = self.reason_for(frontmatter(include_grant=False))
        self.assertIn("no 'grant:' mapping", reason)

    def test_missing_filesystem_write_means_no_edit_authority(self):
        reason = self.reason_for(frontmatter(include_fs=False, shell="allowed"))
        self.assertIn("no file-edit authority", reason)

    def test_missing_shell_mode_means_denied(self):
        reason = self.reason_for(frontmatter(include_shell=False), tool="Bash", command="ls")
        self.assertIn("shell.execute is denied", reason)

    def test_invalid_shell_value_denies(self):
        reason = self.reason_for(frontmatter(shell="yes"), tool="Bash", command="ls")
        self.assertIn("invalid", reason)

    def test_empty_filesystem_write_denies(self):
        reason = self.reason_for(frontmatter(filesystem_write=()))
        self.assertIn("is empty", reason)

    def test_mutation_requires_one_exact_active_status(self):
        valid = frontmatter()
        cases = {
            "missing": valid.replace("status: ACTIVE\n", ""),
            "duplicate": valid.replace("status: ACTIVE\n",
                                       "status: ACTIVE\nstatus: ACTIVE\n"),
            "malformed": valid.replace("status: ACTIVE", "status: [ACTIVE]"),
            "commented": valid.replace("status: ACTIVE", "# status: ACTIVE"),
            "different-case": valid.replace("status: ACTIVE", "status: active"),
            "unmatched-quote": valid.replace("status: ACTIVE", "status: 'ACTIVE"),
            "non-active": valid.replace("status: ACTIVE", "status: COMPLETE"),
        }
        for label, text in cases.items():
            with self.subTest(case=label):
                denial = self.reason_for(text)
                self.assertIsNotNone(denial)
                self.assertEqual(denial.code, "work_order_status_invalid")

    def test_active_status_cannot_coexist_with_retirement_metadata(self):
        for metadata in ("void: true", "superseded_by: WO-PL-901",
                         "void : true", "superseded_by : WO-PL-901"):
            with self.subTest(metadata=metadata):
                text = frontmatter().replace(
                    "status: ACTIVE\n", f"status: ACTIVE\n{metadata}\n", 1)
                denial = self.reason_for(text)
                self.assertIsNotNone(denial)
                self.assertEqual(denial.code, "work_order_status_invalid")

    def test_runtime_rejects_grant_shapes_the_dispatch_parser_rejects(self):
        cases = {
            "duplicate-child": (
                "grant:\n"
                "  filesystem.write: [safe.txt]\n"
                "  filesystem.write: [unsafe.txt]\n"
                "  filesystem.read.deny: [archive/**]\n"
                "  shell.execute: denied\n"
                "  network.egress: denied\n"
            ),
            "duplicate-mapping": (
                "grant:\n"
                "  filesystem.write: [safe.txt]\n"
                "  filesystem.read.deny: [archive/**]\n"
                "  shell.execute: denied\n"
                "  network.egress: denied\n"
                "grant:\n"
                "  filesystem.write: [unsafe.txt]\n"
                "  filesystem.read.deny: []\n"
                "  shell.execute: allowed\n"
                "  network.egress: allowed\n"
            ),
            "scalar-mapping": (
                "grant: malformed\n"
                "  filesystem.write: [unsafe.txt]\n"
                "  filesystem.read.deny: []\n"
                "  shell.execute: allowed\n"
                "  network.egress: allowed\n"
            ),
            "scalar-write-list": (
                "grant:\n"
                "  filesystem.write: 'unsafe.txt\n"
                "  filesystem.read.deny: [archive/**]\n"
                "  shell.execute: denied\n"
                "  network.egress: denied\n"
            ),
            "unknown-child": (
                "grant:\n"
                "  filesystem.write: [safe.txt]\n"
                "  filesystem.read.deny: [archive/**]\n"
                "  shell.exec: allowed\n"
                "  shell.execute: denied\n"
                "  network.egress: denied\n"
            ),
        }
        for label, grant in cases.items():
            with self.subTest(case=label):
                text = (
                    "---\nid: WO-000\nstatus: ACTIVE\ndoctrine_rev: 0.8\n"
                    f"{grant}---\n"
                )
                denial = self.reason_for(text, file_path="unsafe.txt")
                self.assertIsNotNone(denial)
                self.assertEqual(denial.code, "grant_structure_invalid")

    def test_capability_modes_are_case_sensitive_like_dispatch(self):
        for key, code in (("shell.execute", "shell_execute_invalid"),
                          ("network.egress", "network_egress_invalid")):
            with self.subTest(key=key):
                text = frontmatter().replace(f"{key}: denied", f"{key}: ALLOWED")
                denial = self.reason_for(text)
                self.assertIsNotNone(denial)
                self.assertEqual(denial.code, code)

    def test_block_list_comment_and_unmatched_quote_match_dispatch_scalars(self):
        commented = frontmatter(filesystem_write=("safe.txt # comment",))
        self.assertIsNone(self.reason_for(commented, file_path="safe.txt"))

        unmatched = frontmatter(filesystem_write=("'unsafe.txt",))
        denial = self.reason_for(unmatched, file_path="unsafe.txt")
        self.assertIsNotNone(denial)
        self.assertEqual(denial.code, "write_target_out_of_grant")

    def test_nested_mapping_cannot_replace_the_owner_grant(self):
        text = (
            "---\nid: WO-000\nstatus: ACTIVE\ndoctrine_rev: 0.8\n"
            "grant:\n"
            "  filesystem.write: [governance/scratch/**]\n"
            "  filesystem.read.deny: [governance/history/**]\n"
            "  shell.execute: denied\n"
            "  network.egress: denied\n"
            "  dispatch_validation:\n"
            "    filesystem.write: [src/**]\n"
            "    filesystem.read.deny: []\n"
            "    shell.execute: allowed\n"
            "    network.egress: allowed\n"
            "---\n"
        )
        denial = self.reason_for(text, file_path="src/main.py")
        self.assertIsNotNone(denial)
        self.assertEqual(denial.code, "grant_structure_invalid")


class ShellTests(unittest.TestCase):
    def setUp(self):
        import contextlib
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)

    def test_all_shell_tools_denied_when_shell_denied(self):
        repo = FixtureRepo(self.stack, wo_text=frontmatter(shell="denied"))
        for tool in ("Bash", "PowerShell", "Monitor", "KillShell"):
            with self.subTest(tool=tool):
                reason = wall.decide(event(tool, command="ls"), repo.root)
                self.assertIn("shell.execute is denied", reason)

    def test_shell_modes_cannot_bypass_the_control_plane_floor(self):
        for mode in ("restricted", "allowed"):
            repo = FixtureRepo(self.stack, wo_text=frontmatter(shell=mode))
            for tool in ("Bash", "PowerShell", "Monitor", "KillShell"):
                with self.subTest(mode=mode, tool=tool):
                    denial = wall.decide(event(tool, command="true"), repo.root)
                    self.assertIsNotNone(denial)
                    self.assertEqual(denial.code, "control_plane_channel_uninspectable")

    def test_shell_denied_with_no_work_order(self):
        repo = FixtureRepo(self.stack, write_pointer=False)
        for tool in ("Bash", "PowerShell", "Monitor"):
            with self.subTest(tool=tool):
                reason = wall.decide(event(tool, command="ls"), repo.root)
                self.assertIn("No active work order", reason)


class GrantPathTests(unittest.TestCase):
    def setUp(self):
        import contextlib
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)

    def decide_write(self, entries, target):
        repo = FixtureRepo(self.stack, wo_text=frontmatter(filesystem_write=entries))
        return wall.decide(event("Write", file_path=target), repo.root)

    def test_exact_allowed_file(self):
        self.assertIsNone(self.decide_write(("README.md",), "README.md"))

    def test_exact_file_does_not_grant_siblings(self):
        reason = self.decide_write(("README.md",), "SECRETS.md")
        self.assertIn("outside", reason)

    def test_recursive_subtree_allows_nested(self):
        self.assertIsNone(self.decide_write(
            ("governance/scratch/**",), "governance/scratch/deep/nested/ok.txt"))

    def test_recursive_subtree_allows_direct_child(self):
        self.assertIsNone(self.decide_write(
            ("governance/scratch/**",), "governance/scratch/ok.txt"))

    def test_sibling_prefix_denied_not_string_prefix(self):
        reason = self.decide_write(
            ("governance/scratch/**",), "governance/scratch2/sneaky.txt")
        self.assertIn("outside", reason)

    def test_exact_directory_does_not_imply_recursion(self):
        reason = self.decide_write(("governance/scratch",), "governance/scratch/a.txt")
        self.assertIn("outside", reason)

    def test_single_star_rejected_and_not_recursive(self):
        reason = self.decide_write(("governance/scratch/*",), "governance/scratch/a.txt")
        self.assertIn("unsupported wildcard", reason)

    def test_other_wildcards_rejected(self):
        for entry in ("*.md", "governance/**/scratch", "gov*/scratch/**"):
            with self.subTest(entry=entry):
                reason = self.decide_write((entry,), "governance/scratch/a.txt")
                self.assertIn("unsupported wildcard", reason)

    def test_absolute_grant_path_denied(self):
        for entry in ("/etc/**", "C:/Windows/**"):
            with self.subTest(entry=entry):
                reason = self.decide_write((entry,), "governance/scratch/a.txt")
                self.assertIn("not repository-relative", reason)

    def test_escaping_grant_path_denied(self):
        reason = self.decide_write(("../outside/**",), "governance/scratch/a.txt")
        self.assertIn("escapes the repository", reason)

    def test_backslash_grant_path_denied(self):
        reason = self.decide_write(("governance\\scratch\\**",), "governance/scratch/a.txt")
        self.assertIn("backslash", reason)

    def test_symlinked_grant_base_cannot_widen_scope(self):
        repo = FixtureRepo(self.stack, wo_text=frontmatter(("linked/**",)))
        real = repo.root / "real"
        real.mkdir()
        try:
            (repo.root / "linked").symlink_to(real, target_is_directory=True)
        except OSError:
            self.skipTest("platform refused symlink fixture creation")
        denial = wall.decide(event("Write", file_path="linked/file.txt"), repo.root)
        self.assertIsNotNone(denial)
        self.assertEqual(denial.code, "grant_path_invalid")

    @unittest.skipUnless(sys.platform == "win32", "Windows junction fixture")
    def test_windows_junction_grant_base_cannot_widen_scope(self):
        repo = FixtureRepo(self.stack, wo_text=frontmatter(("junction/**",)))
        real = repo.root / "real-junction-target"
        real.mkdir()
        link = repo.root / "junction"
        created = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(real)],
            capture_output=True, text=True, timeout=30)
        if created.returncode != 0:
            self.skipTest("platform refused junction fixture creation")
        denial = wall.decide(event("Write", file_path="junction/file.txt"), repo.root)
        self.assertIsNotNone(denial)
        self.assertEqual(denial.code, "grant_path_invalid")

    def test_symlinked_write_target_alias_is_rejected(self):
        repo = FixtureRepo(self.stack, wo_text=frontmatter(("real.txt",)))
        real = repo.root / "real.txt"
        real.write_text("original", encoding="utf-8")
        try:
            (repo.root / "alias.txt").symlink_to(real)
        except OSError:
            self.skipTest("platform refused symlink fixture creation")
        denial = wall.decide(event("Write", file_path="alias.txt"), repo.root)
        self.assertIsNotNone(denial)
        self.assertEqual(denial.code, "write_target_path_invalid")

    def test_absolute_target_outside_repo_denied(self):
        import contextlib
        with contextlib.ExitStack() as stack:
            repo = FixtureRepo(stack, wo_text=frontmatter(("governance/scratch/**",)))
            reason = wall.decide(
                event("Write", file_path=outside_repo_target(repo.root)), repo.root)
        self.assertIn("outside", reason)

    def test_target_escaping_repo_denied(self):
        reason = self.decide_write(
            ("governance/scratch/**",), "governance/scratch/../../../escape.txt")
        self.assertEqual(reason.code, "write_target_path_invalid")

    def test_in_repository_parent_traversal_target_is_rejected(self):
        denial = self.decide_write(("README.md",), "governance/../README.md")
        self.assertIsNotNone(denial)
        self.assertEqual(denial.code, "write_target_path_invalid")

    def test_repository_root_write_target_is_rejected(self):
        denial = self.decide_write(("README.md",), ".")
        self.assertIsNotNone(denial)
        self.assertEqual(denial.code, "write_target_path_invalid")

    def test_missing_edit_target_denies(self):
        repo = FixtureRepo(self.stack)
        for payload in ({}, {"command": "ls"}, {"file_path": ""}):
            with self.subTest(payload=payload):
                reason = wall.decide(
                    {"tool_name": "Write", "tool_input": payload}, repo.root)
                self.assertIn("no determinable write target", reason)

    def test_absent_tool_input_denies(self):
        repo = FixtureRepo(self.stack)
        reason = wall.decide({"tool_name": "Edit"}, repo.root)
        self.assertIn("no determinable write target", reason)

    def test_notebook_path_is_a_target(self):
        repo = FixtureRepo(self.stack, wo_text=frontmatter(("governance/scratch/**",)))
        self.assertIsNone(wall.decide(
            event("NotebookEdit", notebook_path="governance/scratch/n.ipynb"), repo.root))


class ProtectedControlPlaneTests(unittest.TestCase):
    def setUp(self):
        import contextlib
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)

    def test_every_file_edit_tool_denies_every_protected_target_even_when_granted(self):
        targets = (
            ".claude/active-wo.txt",
            ".claude/hooks/wo_capability_wall.py",
            ".claude/hooks/disable-wall.py",
            ".claude/settings.json",
            ".claude/settings.local.json",
            "governance/work-orders/WO-000.md",
            "governance/LOG-denials.jsonl",
        )
        repo = FixtureRepo(self.stack, wo_text=frontmatter(targets))
        for tool in sorted(wall.FILE_EDIT_TOOLS):
            key = "notebook_path" if tool == "NotebookEdit" else "file_path"
            for target in targets:
                with self.subTest(tool=tool, target=target):
                    denial = wall.decide(event(tool, **{key: target}), repo.root)
                    self.assertIsNotNone(denial)
                    self.assertEqual(denial.code, "control_plane_protected")

    def test_portable_aliases_deny_for_every_protected_target(self):
        aliases = (
            ".claude/ACTIVE-WO.TXT",
            ".claude/active-wo.txt.",
            ".claude/active-wo.txt ",
            ".claude/HOOKS/alternate.py",
            ".claude/hooks./alternate.py",
            ".claude/Settings.json",
            ".claude/settings.json.",
            ".claude/SETTINGS.LOCAL.JSON ",
            "governance/work-orders/wo-000.md",
            "governance/work-orders/WO-000.md.",
            "governance/LOG-DENIALS.JSONL",
            "governance/LOG-denials.jsonl.",
        )
        repo = FixtureRepo(
            self.stack,
            wo_text=frontmatter((".claude/**", "governance/**")),
        )
        for target in aliases:
            with self.subTest(target=target):
                denial = wall.decide(event("Write", file_path=target), repo.root)
                self.assertIsNotNone(denial)
                self.assertEqual(denial.code, "control_plane_protected")


class ReadDenyTests(unittest.TestCase):
    """WO-PL-012: grant.filesystem.read.deny enforcement for READ_TOOLS."""

    def setUp(self):
        import contextlib
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)

    def repo(self, read_deny=("governance/history/**", "archive/**"), **kwargs):
        wo_text = frontmatter(read_deny=read_deny, **kwargs)
        return FixtureRepo(self.stack, wo_text=wo_text)

    def wo_grant(self, repo):
        wo_path = repo.root / "governance" / "work-orders" / "WO-000.md"
        text = wo_path.read_text(encoding="utf-8")
        return wall.parse_grant(wall.extract_frontmatter(text))

    # -- 1. parser currently ignores filesystem.read.deny -----------------

    def test_parser_parses_block_read_deny(self):
        repo = self.repo()
        grant = self.wo_grant(repo)
        self.assertEqual(grant["filesystem.read.deny"],
                          ["governance/history/**", "archive/**"])

    def test_parser_parses_inline_read_deny(self):
        text = ("---\nid: WO-000\nstatus: ACTIVE\ndoctrine_rev: 0.8\n"
                "grant:\n  filesystem.write: [governance/scratch/**]\n"
                "  filesystem.read.deny: [governance/history/**, archive/**]\n"
                "  shell.execute: denied\n  network.egress: denied\n---\n")
        repo = FixtureRepo(self.stack, wo_text=text)
        wo_path = repo.root / "governance" / "work-orders" / "WO-000.md"
        grant = wall.parse_grant(wall.extract_frontmatter(wo_path.read_text(encoding="utf-8")))
        self.assertEqual(grant["filesystem.read.deny"],
                          ["governance/history/**", "archive/**"])

    # -- 2. Read can currently open a file under a denied subtree ---------

    def test_read_under_denied_subtree_is_denied(self):
        repo = self.repo()
        denial = wall.decide(
            event("Read", file_path="governance/history/secret.md"), repo.root)
        self.assertIsNotNone(denial, "Read must be denied under a denied read subtree")

    def test_notebook_read_under_denied_subtree_is_denied(self):
        repo = self.repo()
        denial = wall.decide(
            event("NotebookRead", notebook_path="archive/old.ipynb"), repo.root)
        self.assertIsNotNone(denial)

    # -- 3. Grep/Glob rooted at an ancestor traverse a denied subtree -----

    def test_grep_rooted_at_ancestor_of_denied_subtree_is_denied(self):
        repo = self.repo()
        denial = wall.decide(event("Grep", pattern="x", path="governance"), repo.root)
        self.assertIsNotNone(denial)

    def test_glob_omitted_root_defaults_to_repository_root_and_is_denied(self):
        repo = self.repo()
        denial = wall.decide(event("Glob", pattern="**/*.md"), repo.root)
        self.assertIsNotNone(
            denial, "omitted traversal root means repository root")

    def test_search_pattern_cannot_escape_its_root_around_read_deny(self):
        repo = self.repo(read_deny=("secret/**",))
        calls = (
            event("Glob", path="docs", pattern="../secret/*"),
            event("Grep", path="docs", pattern="needle", glob="../secret/*"),
        )
        for call in calls:
            with self.subTest(tool=call["tool_name"]):
                denial = wall.decide(call, repo.root)
                self.assertIsNotNone(denial)
                self.assertEqual(denial.code, "read_pattern_invalid")

    def test_search_pattern_grammar_rejects_unprovable_confinement(self):
        repo = self.repo(read_deny=("secret/**",))
        patterns = (
            "{../secret/*,*}",
            "{..}/secret/*",
            ".[.]/secret/*",
            ".?/secret/*",
            "~/secret/*",
            "C:/secret/*",
            "\\\\server\\secret\\*",
        )
        for pattern in patterns:
            for call in (
                event("Glob", path="docs", pattern=pattern),
                event("Grep", path="docs", pattern="needle", glob=pattern),
            ):
                with self.subTest(tool=call["tool_name"], pattern=pattern):
                    denial = wall.decide(call, repo.root)
                    self.assertIsNotNone(denial)
                    self.assertEqual(denial.code, "read_pattern_invalid")

    def test_search_pattern_grammar_keeps_confined_common_forms(self):
        repo = self.repo(read_deny=("secret/**",))
        for pattern in ("*.py", "**/*.md", "safe/file?.txt", "src/**/test_*.py"):
            with self.subTest(pattern=pattern):
                self.assertIsNone(wall.decide(
                    event("Glob", path="docs", pattern=pattern), repo.root))

    def test_ls_rooted_inside_denied_subtree_is_denied(self):
        repo = self.repo()
        denial = wall.decide(event("LS", path="governance/history"), repo.root)
        self.assertIsNotNone(denial)

    # -- 4. an allowed sibling file/read root remains readable ------------

    def test_sibling_read_root_remains_allowed(self):
        repo = self.repo()
        self.assertIsNone(wall.decide(event("Read", file_path="README.md"), repo.root))
        self.assertIsNone(
            wall.decide(event("Grep", pattern="x", path="adapters"), repo.root))
        self.assertIsNone(
            wall.decide(event("Glob", pattern="*.py", path="adapters"), repo.root))

    def test_no_read_deny_declared_allows_everything(self):
        repo = self.repo(read_deny=None)
        self.assertIsNone(wall.decide(event("Read", file_path="anything.md"), repo.root))
        self.assertIsNone(wall.decide(event("Glob", pattern="**/*"), repo.root))

    def test_absent_pointer_still_allows_ordinary_read_only_review(self):
        repo = FixtureRepo(self.stack, write_pointer=False)
        self.assertIsNone(wall.decide(
            event("Read", file_path="README.md"), repo.root))

    def test_existing_nonfile_pointer_fails_closed_for_reads(self):
        repo = FixtureRepo(self.stack, write_pointer=False)
        (repo.root / ".claude" / "active-wo.txt").mkdir()
        denial = wall.decide(event("Read", file_path="README.md"), repo.root)
        self.assertIsNotNone(denial)
        self.assertEqual(denial.code, "pointer_not_regular")

    def test_malformed_pointed_work_order_fails_closed_for_reads(self):
        cases = (
            ("not frontmatter\n", "frontmatter_missing_open_fence"),
            ("---\nid: WO-000\nstatus: ACTIVE\n---\n", "grant_missing"),
            (frontmatter().replace("  shell.execute: denied\n",
                                   "    nested: invalid\n"),
             "grant_structure_invalid"),
        )
        for text, code in cases:
            with self.subTest(code=code):
                repo = FixtureRepo(self.stack, wo_text=text)
                denial = wall.decide(
                    event("Read", file_path="README.md"), repo.root)
                self.assertIsNotNone(denial)
                self.assertEqual(denial.code, code)
                self.assertNotEqual(denial.safe_reason, "Denied.")

    def test_invalid_write_grant_path_fails_closed_for_reads(self):
        repo = FixtureRepo(
            self.stack,
            wo_text=frontmatter(
                filesystem_write=("../outside/**",),
                read_deny=None,
            ),
        )
        denial = wall.decide(event("Read", file_path="README.md"), repo.root)
        self.assertIsNotNone(denial)
        self.assertEqual(denial.code, "grant_path_invalid")

    # -- 5. malformed or escaping deny entries fail closed -----------------

    def test_malformed_read_deny_entry_fails_closed(self):
        for entry in ("governance\\history\\**", "gov*/history/**", "../outside/**"):
            with self.subTest(entry=entry):
                repo = self.repo(read_deny=(entry,))
                denial = wall.decide(event("Read", file_path="README.md"), repo.root)
                self.assertIsNotNone(denial, entry)

    def test_escaping_read_target_fails_closed(self):
        repo = self.repo()
        denial = wall.decide(
            event("Read", file_path="governance/scratch/../../../escape.txt"), repo.root)
        self.assertIsNotNone(denial)

    def test_absolute_read_target_outside_repository_fails_closed(self):
        repo = self.repo()
        denial = wall.decide(
            event("Read", file_path=outside_repo_target(repo.root)), repo.root)
        self.assertIsNotNone(denial)

    def test_undeterminable_read_target_fails_closed(self):
        repo = self.repo()
        denial = wall.decide({"tool_name": "Read", "tool_input": {}}, repo.root)
        self.assertIsNotNone(denial)

    # -- 6. safe denial-log output --------------------------------------

    def test_read_denial_log_excludes_path_pattern_and_sentinel(self):
        repo = self.repo()
        denial = wall.decide(
            event("Read", file_path="governance/history/sentinel.txt"), repo.root)
        self.assertIsNotNone(denial)
        wall.log_denial(repo.root, denial, tool="Read",
                        timestamp=FIXED_TS, session_id=FIXED_SESSION)

        denial2 = wall.decide(
            event("Grep", pattern="TOP-SECRET-MARKER", path="governance/history"),
            repo.root)
        self.assertIsNotNone(denial2)
        wall.log_denial(repo.root, denial2, tool="Grep",
                        timestamp=FIXED_TS, session_id=FIXED_SESSION)

        raw = (repo.root / "governance" / "LOG-denials.jsonl").read_text(encoding="utf-8")
        for forbidden in ("sentinel.txt", "TOP-SECRET-MARKER", "governance/history",
                          "governance\\history"):
            self.assertNotIn(forbidden, raw, f"denial log leaked {forbidden!r}")


class InlineGrantSyntaxTests(unittest.TestCase):
    def setUp(self):
        import contextlib
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)

    def test_inline_list_parsed(self):
        text = ("---\nid: WO-000\nstatus: ACTIVE\ndoctrine_rev: 0.8\n"
                "grant:\n  filesystem.write: [governance/scratch/**, README.md]\n"
                "  shell.execute: denied\n  network.egress: denied\n---\n")
        repo = FixtureRepo(self.stack, wo_text=text)
        self.assertIsNone(wall.decide(
            event("Write", file_path="governance/scratch/a.txt"), repo.root))
        self.assertIsNone(wall.decide(event("Write", file_path="README.md"), repo.root))
        self.assertIn("outside", wall.decide(
            event("Write", file_path="other.md"), repo.root))

    def test_comment_after_shell_value_ignored(self):
        text = ("---\nid: WO-000\nstatus: ACTIVE\ndoctrine_rev: 0.8\n"
                "grant:\n  filesystem.write:\n    - README.md\n"
                "  shell.execute: allowed   # denied | restricted | allowed\n"
                "  network.egress: denied\n---\n")
        repo = FixtureRepo(self.stack, wo_text=text)
        wo_path = repo.root / "governance" / "work-orders" / "WO-000.md"
        grant = wall.parse_grant(wall.extract_frontmatter(
            wo_path.read_text(encoding="utf-8")))
        self.assertEqual(grant["shell.execute"], "allowed")

    def test_hash_inside_inline_path_does_not_erase_read_denies(self):
        text = (
            "---\nid: WO-000\nstatus: ACTIVE\ndoctrine_rev: 0.8\n"
            "grant:\n  filesystem.write: [governance/scratch/**]\n"
            "  filesystem.read.deny: [secret/c#sharp/**, secret/**]\n"
            "  shell.execute: denied\n  network.egress: denied\n---\n"
        )
        repo = FixtureRepo(self.stack, wo_text=text)
        for target in ("secret/c#sharp/key.txt", "secret/keys.txt"):
            with self.subTest(target=target):
                denial = wall.decide(event("Read", file_path=target), repo.root)
                self.assertIsNotNone(denial)
                self.assertEqual(denial.code, "read_target_denied")


class ProcessFallbackTests(unittest.TestCase):
    """Invalid input and unexpected exceptions must exit 2, never exit 1.

    The adapter is installed into a temporary tree at the location it occupies
    in a real project, <root>/.claude/hooks/, so that its own repository_root()
    resolves to the fixture and any denial log it writes lands there. Running
    it from its canonical path would make it write into this repository.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        hooks = self.tmp / ".claude" / "hooks"
        hooks.mkdir(parents=True)
        self.installed = hooks / "wo_capability_wall.py"
        self.installed.write_bytes(ADAPTER_PATH.read_bytes())

    def run_adapter(self, stdin_text, *, include_project_dir=True):
        env = None
        if include_project_dir:
            env = dict(__import__("os").environ)
            env["CLAUDE_PROJECT_DIR"] = str(self.tmp)
        return subprocess.run(
            [sys.executable, str(self.installed)],
            input=stdin_text, capture_output=True, text=True, timeout=60,
            env=env)

    def test_misplaced_installation_fails_hard_without_creating_governance(self):
        misplaced = self.tmp / "wo_capability_wall.py"
        misplaced.write_bytes(ADAPTER_PATH.read_bytes())
        result = subprocess.run(
            [sys.executable, str(misplaced)],
            input=json.dumps(event("Write", file_path="README.md")),
            capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse((self.tmp.parent / "governance").exists())

    def test_shape_correct_copy_without_project_root_fails_before_logging(self):
        result = self.run_adapter(
            json.dumps(event("Write", file_path="README.md")),
            include_project_dir=False,
        )
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("CLAUDE_PROJECT_DIR", result.stderr)
        self.assertFalse((self.tmp / "governance").exists())

    def test_denial_log_stays_inside_the_installed_repository(self):
        """The adapter must write its denial log under the repository it is
        installed in, never under this one.

        This repository now has its own governance/ directory (self-adoption),
        so the invariant is that running the adapter leaves that directory's
        denial log byte-for-byte unchanged. Asserting governance/ does not
        exist would test the wrong thing and would break on adoption.
        """
        our_log = REPO_ROOT / "governance" / LOG_NAME
        before = our_log.read_bytes() if our_log.is_file() else None
        legacy = REPO_ROOT / "governance" / "LOG-denials.txt"
        legacy_before = legacy.read_bytes() if legacy.is_file() else None

        result = self.run_adapter("[1, 2, 3]")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.tmp / "governance" / LOG_NAME).is_file(),
                        "the adapter did not log under its own installed repository")
        after = our_log.read_bytes() if our_log.is_file() else None
        self.assertEqual(after, before,
                         "the adapter wrote a denial log into the source repository")
        legacy_after = legacy.read_bytes() if legacy.is_file() else None
        self.assertEqual(legacy_after, legacy_before,
                         "the adapter resurrected the retired raw denial log")

    def test_preflight_is_read_only_and_verifies_portable_project_registration(self):
        platform_name = "windows" if sys.platform == "win32" else "posix"
        interpreter = "py -3" if platform_name == "windows" else "python3"
        settings = self.tmp / ".claude" / "settings.json"
        settings.write_text(json.dumps({"hooks": {"PreToolUse": [{
            "matcher": "*",
            "hooks": [{
                "type": "command",
                "command": f"{interpreter} \"${{CLAUDE_PROJECT_DIR}}/.claude/hooks/wo_capability_wall.py\"",
                "timeout": 10,
            }],
        }]}}), encoding="utf-8", newline="\n")
        digest = hashlib.sha256(self.installed.read_bytes()).hexdigest()
        log = self.tmp / "governance" / LOG_NAME
        result = subprocess.run([
            sys.executable, str(self.installed), "--preflight",
            "--project-root", str(self.tmp),
            "--settings", str(settings),
            "--expected-digest", digest,
            "--platform", platform_name,
        ], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["matcher"], "*")
        self.assertEqual(payload["source"], "project")
        self.assertTrue(payload["portable_registration"])
        self.assertEqual(payload["timeout_seconds"], 10)
        self.assertFalse(log.exists(), "preflight must not append denial evidence")

    def test_supported_python_range_is_explicit_and_closed(self):
        self.assertFalse(wall.supported_python_version((3, 9)))
        for minor in range(10, 15):
            with self.subTest(minor=minor):
                self.assertTrue(wall.supported_python_version((3, minor)))
        self.assertFalse(wall.supported_python_version((3, 15)))
        self.assertFalse(wall.supported_python_version((4, 0)))

    def test_preflight_rejects_digest_platform_timeout_and_nonportable_command(self):
        settings = self.tmp / ".claude" / "settings.json"
        digest = hashlib.sha256(self.installed.read_bytes()).hexdigest()
        native = "windows" if sys.platform == "win32" else "posix"
        other = "posix" if native == "windows" else "windows"
        interpreter = "py -3" if native == "windows" else "python3"

        def run(*, expected=digest, platform=native, command=None, timeout=10):
            hook = {
                "type": "command",
                "command": command or (
                    f'{interpreter} "${{CLAUDE_PROJECT_DIR}}/.claude/hooks/'
                    'wo_capability_wall.py"'),
            }
            if timeout is not None:
                hook["timeout"] = timeout
            settings.write_text(json.dumps({"hooks": {"PreToolUse": [{
                "matcher": "*", "hooks": [hook],
            }]}}), encoding="utf-8", newline="\n")
            return subprocess.run([
                sys.executable, str(self.installed), "--preflight",
                "--project-root", str(self.tmp), "--settings", str(settings),
                "--expected-digest", expected, "--platform", platform,
            ], capture_output=True, text=True, timeout=60)

        cases = (
            ("digest", run(expected="0" * 64)),
            ("platform", run(platform=other)),
            ("timeout", run(timeout=None)),
            ("portable", run(command=f'{interpreter} "C:/fixed/hook.py"')),
        )
        for label, result in cases:
            with self.subTest(case=label):
                self.assertEqual(result.returncode, 2)
                self.assertIn("preflight", result.stderr.lower())
        self.assertFalse((self.tmp / "governance" / LOG_NAME).exists())

    def test_malformed_stdin_exits_2(self):
        result = self.run_adapter("this is not json")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("wo_capability_wall", result.stderr)

    def test_empty_stdin_exits_2(self):
        result = self.run_adapter("")
        self.assertEqual(result.returncode, 2, result.stderr)

    def test_non_object_json_denies_rather_than_crashing(self):
        result = self.run_adapter("[1, 2, 3]")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(
            payload["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_unexpected_exception_exits_2(self):
        module = load_adapter()

        def boom(_event, _root):
            raise RuntimeError("injected")

        module.decide = boom
        module.repository_root = lambda: REPO_ROOT
        module.sys = sys
        original_stdin = sys.stdin
        original_stderr = sys.stderr
        sys.stdin = io.StringIO(json.dumps(event("Write", file_path="x")))
        sys.stderr = io.StringIO()
        try:
            with self.assertRaises(SystemExit) as caught:
                module.main()
            self.assertEqual(caught.exception.code, 2)
        finally:
            sys.stdin = original_stdin
            sys.stderr = original_stderr

    def test_deliberate_systemexit_is_preserved(self):
        module = load_adapter()

        def clean_exit(_event, _root):
            raise SystemExit(0)

        module.decide = clean_exit
        module.repository_root = lambda: REPO_ROOT
        original_stdin = sys.stdin
        sys.stdin = io.StringIO(json.dumps(event("Write", file_path="x")))
        try:
            with self.assertRaises(SystemExit) as caught:
                module.main()
            self.assertEqual(caught.exception.code, 0)
        finally:
            sys.stdin = original_stdin


class DenyPayloadTests(unittest.TestCase):
    def test_deny_emits_valid_hook_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / ".claude").mkdir()
            denial = wall.decide(event("Write", file_path="a.txt"), root)
            self.assertIsNotNone(denial)
            self.assertIn("No active work order", denial)
            wall.log_denial(root, denial, tool="Write", timestamp=FIXED_TS,
                            session_id=FIXED_SESSION)
            log = root / "governance" / LOG_NAME
            self.assertTrue(log.is_file())
            record = json.loads(log.read_text(encoding="utf-8").strip())
            self.assertEqual(record["reason_code"], "no_active_work_order")
            self.assertEqual(record["decision"], "deny")


# --------------------------------------------------------------------------
# Structured denial log (WO-PL-005 section 3)
# --------------------------------------------------------------------------

FIXED_TS = "2026-08-16T20:06:22Z"
FIXED_SESSION = "sess-fixture-0001"

RECORD_FIELDS = ["schema", "timestamp", "session_id", "tool", "surface",
                 "work_order", "decision", "reason_code", "reason"]


class StructuredDenialLogTests(unittest.TestCase):
    """Time and session are injected, never asserted from a live clock."""

    def setUp(self):
        import contextlib
        self.stack = contextlib.ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory())).resolve()
        (self.root / ".claude").mkdir()

    def log_path(self):
        return self.root / "governance" / LOG_NAME

    def write(self, denial, tool=None, session_id=FIXED_SESSION):
        wall.log_denial(self.root, denial, tool=tool, timestamp=FIXED_TS,
                        session_id=session_id)

    def deny(self, tool="Write", **tool_input):
        if not tool_input:
            tool_input = {"file_path": "a.txt"}
        denial = wall.decide(event(tool, **tool_input), self.root)
        self.assertIsNotNone(denial)
        return denial

    def records(self):
        text = self.log_path().read_text(encoding="utf-8")
        return [json.loads(line) for line in text.splitlines() if line]

    # -- shape ------------------------------------------------------------

    def test_every_record_is_one_line_of_valid_json(self):
        for tool in ("Write", "Bash", "Agent", "mcp__x__y"):
            self.write(self.deny(tool, file_path="a.txt", command="ls"), tool=tool)
        raw = self.log_path().read_bytes().decode("utf-8")
        lines = raw.split("\n")
        self.assertEqual(lines[-1], "", "log must end with a terminator")
        for line in lines[:-1]:
            parsed = json.loads(line)
            self.assertIsInstance(parsed, dict)
            self.assertNotIn("\n", line)
        self.assertEqual(len(lines) - 1, 4)

    def test_output_is_lf_only_on_every_platform(self):
        self.write(self.deny(), tool="Write")
        self.write(self.deny(), tool="Write")
        raw = self.log_path().read_bytes()
        self.assertEqual(raw.count(b"\r"), 0, "denial log must never carry CR")
        self.assertEqual(raw.count(b"\n"), 2)

    def test_record_carries_exactly_the_declared_fields(self):
        self.write(self.deny(), tool="Write")
        record = self.records()[0]
        self.assertEqual(list(record.keys()), RECORD_FIELDS)

    def test_schema_version_and_decision_are_fixed(self):
        self.write(self.deny(), tool="Write")
        record = self.records()[0]
        self.assertEqual(record["schema"], wall.SCHEMA_VERSION)
        self.assertEqual(record["decision"], "deny")
        self.assertEqual(record["timestamp"], FIXED_TS)
        self.assertEqual(record["session_id"], FIXED_SESSION)

    # -- optional provider fields -----------------------------------------

    def test_missing_session_id_is_null_not_absent(self):
        self.write(self.deny(), tool="Write", session_id=None)
        record = self.records()[0]
        self.assertIn("session_id", record)
        self.assertIsNone(record["session_id"])

    def test_session_identifier_extraction(self):
        self.assertIsNone(wall.session_identifier({}))
        self.assertIsNone(wall.session_identifier({"session_id": ""}))
        self.assertIsNone(wall.session_identifier({"session_id": 42}))
        self.assertIsNone(wall.session_identifier("not a dict"))
        self.assertEqual(wall.session_identifier({"session_id": " abc "}), "abc")

    def test_unusable_tool_name_is_null(self):
        denial = wall.decide({"tool_name": None}, self.root)
        self.write(denial, tool=None)
        record = self.records()[0]
        self.assertIsNone(record["tool"])
        self.assertEqual(record["surface"], "unmodeled")

    def test_work_order_null_when_unresolvable(self):
        self.write(self.deny(), tool="Write")
        self.assertIsNone(self.records()[0]["work_order"])

    def test_work_order_recorded_repository_relative_when_resolvable(self):
        import contextlib
        with contextlib.ExitStack() as stack:
            repo = FixtureRepo(stack, wo_text=frontmatter(("README.md",)))
            denial = wall.decide(event("Write", file_path="nope.txt"), repo.root)
            self.assertIsNotNone(denial)
            wall.log_denial(repo.root, denial, tool="Write", timestamp=FIXED_TS)
            record = json.loads(
                (repo.root / "governance" / LOG_NAME).read_text(encoding="utf-8").strip())
            self.assertEqual(record["work_order"],
                             "governance/work-orders/WO-000.md")
            self.assertFalse(Path(record["work_order"]).is_absolute())

    # -- stable reason codes ----------------------------------------------

    def test_reason_codes_are_stable_and_mapped(self):
        cases = {
            "no_active_work_order": lambda: wall.decide(
                event("Write", file_path="a.txt"), self.root),
            "tool_not_modeled": lambda: wall.decide(event("Agent"), self.root),
            "hook_event_malformed": lambda: wall.decide([1, 2, 3], self.root),
        }
        for expected, produce in cases.items():
            with self.subTest(code=expected):
                self.assertEqual(produce().code, expected)

    def test_every_reason_code_has_a_safe_sentence(self):
        import contextlib
        seen = set()
        with contextlib.ExitStack() as stack:
            probes = [
                (FixtureRepo(stack, write_pointer=False), event("Write", file_path="a.txt")),
                (FixtureRepo(stack, pointer="   \n"), event("Write", file_path="a.txt")),
                (FixtureRepo(stack, pointer="C:/evil/WO.md"), event("Write", file_path="a.txt")),
                (FixtureRepo(stack, pointer="governance\\work-orders\\WO-000.md"),
                 event("Write", file_path="a.txt")),
                (FixtureRepo(stack, pointer="governance/work-orders/../../x.md"),
                 event("Write", file_path="a.txt")),
                (FixtureRepo(stack, pointer="bootstrap/WO.md"), event("Write", file_path="a.txt")),
                (FixtureRepo(stack, pointer="governance/work-orders/WO.txt"),
                 event("Write", file_path="a.txt")),
                (FixtureRepo(stack, pointer="governance/work-orders/MISSING.md", write_wo=False),
                 event("Write", file_path="a.txt")),
                (FixtureRepo(stack, wo_text="no fence\n"), event("Write", file_path="a.txt")),
                (FixtureRepo(stack, wo_text="---\ngrant:\n"), event("Write", file_path="a.txt")),
                (FixtureRepo(stack, wo_text=frontmatter(include_grant=False)),
                 event("Write", file_path="a.txt")),
                (FixtureRepo(stack, wo_text=frontmatter(shell="denied")),
                 event("Bash", command="ls")),
                (FixtureRepo(stack, wo_text=frontmatter(shell="yes")),
                 event("Bash", command="ls")),
                (FixtureRepo(stack, wo_text=frontmatter(include_fs=False, shell="allowed")),
                 event("Write", file_path="a.txt")),
                (FixtureRepo(stack, wo_text=frontmatter(filesystem_write=())),
                 event("Write", file_path="a.txt")),
                (FixtureRepo(stack, wo_text=frontmatter(filesystem_write=("gov*/**",))),
                 event("Write", file_path="a.txt")),
                (FixtureRepo(stack), {"tool_name": "Write", "tool_input": {}}),
                (FixtureRepo(stack), event("Write", file_path="nope.txt")),
                (FixtureRepo(stack), event("Agent")),
                (FixtureRepo(stack, wo_text=frontmatter(status="COMPLETE")),
                 event("Write", file_path="governance/scratch/a.txt")),
                (FixtureRepo(stack, wo_text=frontmatter(network="denied")),
                 event("WebSearch", query="fixture")),
                (FixtureRepo(stack, wo_text=frontmatter(network="sometimes")),
                 event("WebFetch", url="https://example.invalid")),
                (FixtureRepo(stack, wo_text=frontmatter(shell="allowed")),
                 event("Bash", command="true")),
                (FixtureRepo(stack, wo_text=frontmatter((".claude/active-wo.txt",))),
                 event("Write", file_path=".claude/active-wo.txt")),
                (FixtureRepo(stack, wo_text=frontmatter(("README.md",))),
                 event("Write", file_path="governance/../README.md")),
            ]
            dir_repo = FixtureRepo(stack, pointer="governance/work-orders/adir.md")
            (dir_repo.root / "governance" / "work-orders" / "adir.md").mkdir()
            probes.append((dir_repo, event("Write", file_path="a.txt")))

            nonfile_pointer_repo = FixtureRepo(stack, write_pointer=False)
            (nonfile_pointer_repo.root / ".claude" / "active-wo.txt").mkdir()
            probes.append((nonfile_pointer_repo,
                           event("Read", file_path="README.md")))

            read_deny_repo = FixtureRepo(
                stack, wo_text=frontmatter(read_deny=("governance/history/**",)))
            probes.append((read_deny_repo,
                          event("Read", file_path="governance/history/x.md")))
            probes.append((read_deny_repo,
                          event("Grep", pattern="x", path="governance")))
            probes.append((read_deny_repo, {"tool_name": "Read", "tool_input": {}}))
            probes.append((read_deny_repo,
                          event("Read", file_path=outside_repo_target(read_deny_repo.root))))
            malformed_read_deny_repo = FixtureRepo(
                stack, wo_text=frontmatter(read_deny=("gov*/history/**",)))
            probes.append((malformed_read_deny_repo,
                          event("Read", file_path="README.md")))
            malformed_grant_repo = FixtureRepo(
                stack,
                wo_text=frontmatter().replace(
                    "  shell.execute: denied\n", "    nested: invalid\n"),
            )
            probes.append((malformed_grant_repo,
                           event("Read", file_path="README.md")))
            probes.append((
                FixtureRepo(stack, wo_text=frontmatter(read_deny=("secret/**",))),
                event("Glob", path="docs", pattern="{../secret/*,*}"),
            ))

            for repo, ev in probes:
                denial = wall.decide(ev, repo.root)
                self.assertIsNotNone(denial, ev)
                seen.add(denial.code)
                self.assertIn(denial.code, wall.SAFE_REASONS, denial.code)
                self.assertTrue(denial.safe_reason)
                self.assertNotEqual(denial.safe_reason, "Denied.")
        # Every code the adapter can emit is exercised above except the two
        # I/O-error paths, which are covered separately.
        untested = set(wall.SAFE_REASONS) - seen - {
            "pointer_unreadable", "work_order_unreadable",
            "pointer_names_no_file", "hook_event_malformed"}
        self.assertEqual(untested, set(), f"unexercised reason codes: {untested}")

    # -- privacy ----------------------------------------------------------

    def test_log_never_carries_tool_arguments_or_absolute_paths(self):
        import contextlib
        secret_target = "C:/Users/someone/secret-token-file.txt"
        with contextlib.ExitStack() as stack:
            repo = FixtureRepo(stack, wo_text=frontmatter(("README.md",)))
            denial = wall.decide(event("Write", file_path=secret_target), repo.root)
            self.assertIsNotNone(denial)
            # The provider-facing reason may name it; the log must not.
            self.assertIn(secret_target, denial)
            wall.log_denial(repo.root, denial, tool="Write", timestamp=FIXED_TS)
            raw = (repo.root / "governance" / LOG_NAME).read_text(encoding="utf-8")

        for forbidden in (secret_target, "C:/Users", "someone", "secret-token-file",
                          "README.md", str(repo.root)):
            self.assertNotIn(forbidden, raw, f"denial log leaked {forbidden!r}")

    def test_log_never_carries_grant_entries_or_command_text(self):
        import contextlib
        with contextlib.ExitStack() as stack:
            repo = FixtureRepo(
                stack, wo_text=frontmatter(filesystem_write=("/etc/shadow/**",)))
            denial = wall.decide(event("Write", file_path="a.txt"), repo.root)
            wall.log_denial(repo.root, denial, tool="Write", timestamp=FIXED_TS)
            raw = (repo.root / "governance" / LOG_NAME).read_text(encoding="utf-8")
        self.assertNotIn("/etc/shadow", raw)

    def test_no_drive_letter_or_home_path_in_any_safe_reason(self):
        import re
        pattern = re.compile(r"[A-Za-z]:[/\\]|/home/|/Users/")
        for code, sentence in wall.SAFE_REASONS.items():
            with self.subTest(code=code):
                self.assertIsNone(pattern.search(sentence), code)

    # -- fail-closed ------------------------------------------------------

    def test_logging_failure_does_not_open_the_wall(self):
        denial = self.deny()
        # governance/ occupied by a file, so mkdir and open must fail.
        (self.root / "governance").write_text("not a directory", encoding="utf-8")
        wall.log_denial(self.root, denial, tool="Write", timestamp=FIXED_TS)
        self.assertTrue((self.root / "governance").is_file())

    def test_unserializable_record_is_swallowed_not_raised(self):
        denial = self.deny()
        original = wall.denial_record
        try:
            wall.denial_record = lambda *a, **k: {"bad": {1, 2, 3}}
            wall.log_denial(self.root, denial, tool="Write", timestamp=FIXED_TS)
        finally:
            wall.denial_record = original
        self.assertFalse(self.log_path().is_file())

    def test_deny_is_still_emitted_when_logging_fails(self):
        import contextlib
        buffer = io.StringIO()
        denial = self.deny()
        (self.root / "governance").write_text("not a directory", encoding="utf-8")
        wall.log_denial(self.root, denial, tool="Write", timestamp=FIXED_TS)
        with contextlib.redirect_stdout(buffer):
            wall.emit_deny(denial)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(
            payload["hookSpecificOutput"]["permissionDecision"], "deny")

    # -- retired raw log ---------------------------------------------------

    def test_adapter_never_writes_the_retired_raw_log(self):
        self.write(self.deny(), tool="Write")
        self.assertFalse((self.root / "governance" / "LOG-denials.txt").exists())
        self.assertEqual(wall.DENIAL_LOG_RELPATH, ("governance", "LOG-denials.jsonl"))


if __name__ == "__main__":
    unittest.main()
