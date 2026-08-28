# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Public-process tests for the deterministic license checker."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "checks" / "check_licenses.py"


class LicenseCheckerProcessTests(unittest.TestCase):
    def make_repo(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "checks").mkdir()
        (root / "LICENSES").mkdir()
        shutil.copy2(CHECKER, root / "checks" / "check_licenses.py")
        for identifier in ("CC-BY-4.0", "CC0-1.0", "MIT-0", "Apache-2.0"):
            (root / "LICENSES" / f"{identifier}.txt").write_text(
                f"legal code for {identifier}\n", encoding="utf-8"
            )
        shutil.copy2(root / "LICENSES" / "CC-BY-4.0.txt", root / "LICENSE")
        (root / "README.md").write_text("fixture prose\n", encoding="utf-8")
        (root / "REUSE.toml").write_text(
            textwrap.dedent(
                """
                version = 1

                [[annotations]]
                path = ["README.md"]
                SPDX-FileCopyrightText = "2026 HLLMR Ventures LLC"
                SPDX-License-Identifier = "CC-BY-4.0"

                [[exclusions]]
                path = ["LICENSE", "LICENSES/**", "REUSE.toml"]
                reason = "canonical licensing metadata"

                [[exclusions]]
                path = ["dist/**"]
                reason = "aggregate archive validated separately"
                """
            ).lstrip(),
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
        subprocess.run(["git", "add", "--all"], cwd=root, check=True)
        return root

    def run_checker(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / "checks" / "check_licenses.py"),
             "--repo-root", str(root), *extra],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_fixture_passes(self):
        result = self.run_checker(self.make_repo())

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(
            "OK: all tracked project files have deterministic license coverage",
            result.stdout,
        )

    def test_recursive_annotation_covers_nested_files(self):
        root = self.make_repo()
        (root / "docs" / "nested").mkdir(parents=True)
        (root / "docs" / "nested" / "page.md").write_text(
            "nested prose\n", encoding="utf-8"
        )
        with (root / "REUSE.toml").open("a", encoding="utf-8") as handle:
            handle.write(textwrap.dedent(
                """

                [[annotations]]
                path = ["docs/**"]
                SPDX-FileCopyrightText = "2026 HLLMR Ventures LLC"
                SPDX-License-Identifier = "CC-BY-4.0"
                """
            ))
        subprocess.run(["git", "add", "docs/nested/page.md"], cwd=root, check=True)

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_source_tree_without_git_history_passes(self):
        root = self.make_repo()
        hidden_git = root.parent / f"{root.name}-git-hidden"
        (root / ".git").rename(hidden_git)
        self.addCleanup(shutil.rmtree, hidden_git, ignore_errors=True)

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_read_denied_history_is_annotation_only(self):
        root = self.make_repo()
        (root / "archive").mkdir()
        (root / "archive" / "record.md").write_text(
            "# SPDX-License-Identifier: ID\nprivate historical prose\n",
            encoding="utf-8",
        )
        with (root / "REUSE.toml").open("a", encoding="utf-8") as handle:
            handle.write(textwrap.dedent(
                """

                [[annotations]]
                path = ["archive/**"]
                SPDX-FileCopyrightText = "2026 HLLMR Ventures LLC"
                SPDX-License-Identifier = "CC-BY-4.0"
                """
            ))
        subprocess.run(["git", "add", "archive/record.md"], cwd=root, check=True)

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_new_tracked_unmapped_file_fails(self):
        root = self.make_repo()
        (root / "notes.bin").write_bytes(b"unmapped\n")
        subprocess.run(["git", "add", "notes.bin"], cwd=root, check=True)

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[coverage] notes.bin has no license declaration", result.stdout)

    def test_all_files_mode_catches_untracked_unmapped_file(self):
        root = self.make_repo()
        (root / "notes.bin").write_bytes(b"untracked and unmapped\n")

        result = self.run_checker(root, "--all-files")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[coverage] notes.bin has no license declaration", result.stdout)

    def test_removed_mapping_fails(self):
        root = self.make_repo()
        metadata = (root / "REUSE.toml").read_text(encoding="utf-8")
        (root / "REUSE.toml").write_text(
            metadata.replace('path = ["README.md"]', 'path = ["OTHER.md"]'),
            encoding="utf-8",
        )

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[coverage] README.md has no license declaration", result.stdout)

    def test_conflicting_annotations_fail(self):
        root = self.make_repo()
        with (root / "REUSE.toml").open("a", encoding="utf-8") as handle:
            handle.write(textwrap.dedent(
                """

                [[annotations]]
                path = ["README.md"]
                SPDX-FileCopyrightText = "2026 HLLMR Ventures LLC"
                SPDX-License-Identifier = "CC0-1.0"
                """
            ))

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[conflict] README.md resolves to multiple licenses: CC-BY-4.0, CC0-1.0",
            result.stdout,
        )

    def test_header_conflicting_with_annotation_fails(self):
        root = self.make_repo()
        (root / "scripts").mkdir()
        (root / "scripts" / "tool.py").write_text(
            "# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC\n"
            "# SPDX-License-Identifier: Apache-2.0\n"
            "print('x')\n",
            encoding="utf-8",
        )
        with (root / "REUSE.toml").open("a", encoding="utf-8") as handle:
            handle.write(textwrap.dedent(
                """

                [[annotations]]
                path = ["scripts/**"]
                SPDX-FileCopyrightText = "2026 HLLMR Ventures LLC"
                SPDX-License-Identifier = "MIT-0"
                """
            ))
        subprocess.run(["git", "add", "scripts/tool.py"], cwd=root, check=True)

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[conflict] scripts/tool.py resolves to multiple licenses: "
            "Apache-2.0, MIT-0",
            result.stdout,
        )

    def test_unsupported_identifier_fails(self):
        root = self.make_repo()
        metadata = (root / "REUSE.toml").read_text(encoding="utf-8")
        (root / "REUSE.toml").write_text(
            metadata.replace('SPDX-License-Identifier = "CC-BY-4.0"',
                             'SPDX-License-Identifier = "GPL-3.0-only"'),
            encoding="utf-8",
        )

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[identifier] README.md uses unsupported SPDX identifier GPL-3.0-only",
            result.stdout,
        )

    def test_declared_identifier_requires_legal_code(self):
        root = self.make_repo()
        (root / "LICENSES" / "Apache-2.0.txt").unlink()

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[legal-code] Apache-2.0 has no canonical LICENSES/Apache-2.0.txt",
            result.stdout,
        )

    def test_root_license_must_match_cc_by_code(self):
        root = self.make_repo()
        (root / "LICENSE").write_text("different\n", encoding="utf-8")

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[legal-code] LICENSE differs from LICENSES/CC-BY-4.0.txt",
            result.stdout,
        )

    def test_spdx_template_control_markers_in_legal_code_fail(self):
        root = self.make_repo()
        marker = "<" + "<beginOptional;name=fixture>>"
        cc_by = root / "LICENSES" / "CC-BY-4.0.txt"
        cc_by.write_text(marker + "\nlegal code\n", encoding="utf-8")
        shutil.copy2(cc_by, root / "LICENSE")

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[legal-code] LICENSES/CC-BY-4.0.txt contains SPDX template controls",
            result.stdout,
        )

    def test_missing_tomllib_reports_python_311_requirement_without_traceback(self):
        root = self.make_repo()
        shadow = root / "shadow"
        shadow.mkdir()
        (shadow / "tomllib.py").write_text(
            "raise ModuleNotFoundError(\"No module named 'tomllib'\")\n",
            encoding="utf-8",
        )
        environment = dict(__import__("os").environ)
        environment["PYTHONPATH"] = str(shadow)

        result = subprocess.run(
            [sys.executable, str(root / "checks" / "check_licenses.py"),
             "--repo-root", str(root)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("requires Python 3.11 or newer", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_unknown_exclusion_fails(self):
        root = self.make_repo()
        with (root / "REUSE.toml").open("a", encoding="utf-8") as handle:
            handle.write(textwrap.dedent(
                """

                [[exclusions]]
                path = ["secret/**"]
                reason = "not an approved metadata class"
                """
            ))

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[exclusion] unknown exclusion pattern secret/**", result.stdout)

    def test_executable_cannot_be_annotation_only(self):
        root = self.make_repo()
        (root / "scripts").mkdir()
        (root / "scripts" / "tool.py").write_text("print('x')\n", encoding="utf-8")
        with (root / "REUSE.toml").open("a", encoding="utf-8") as handle:
            handle.write(textwrap.dedent(
                """

                [[annotations]]
                path = ["scripts/**"]
                SPDX-FileCopyrightText = "2026 HLLMR Ventures LLC"
                SPDX-License-Identifier = "Apache-2.0"
                """
            ))
        subprocess.run(["git", "add", "scripts/tool.py"], cwd=root, check=True)

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[header] scripts/tool.py must carry in-file Apache-2.0",
            result.stdout,
        )

    def test_prose_cannot_carry_in_file_spdx_header(self):
        root = self.make_repo()
        (root / "README.md").write_text(
            "# SPDX-License-Identifier: CC-BY-4.0\nfixture prose\n",
            encoding="utf-8",
        )

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[header] README.md must use REUSE.toml, not an in-file SPDX header",
            result.stdout,
        )

    def test_prose_code_example_is_not_an_in_file_header(self):
        root = self.make_repo()
        (root / "README.md").write_text(
            "fixture prose\n\nexample:\n# SPDX-License-Identifier: ID\n",
            encoding="utf-8",
        )

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_executable_header_must_match_path_license(self):
        root = self.make_repo()
        (root / "scripts").mkdir()
        (root / "scripts" / "tool.py").write_text(
            "# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC\n"
            "# SPDX-License-Identifier: MIT-0\n"
            "print('x')\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "scripts/tool.py"], cwd=root, check=True)

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[header] scripts/tool.py carries MIT-0, expected Apache-2.0",
            result.stdout,
        )

    def test_executable_header_requires_copyright(self):
        root = self.make_repo()
        (root / "scripts").mkdir()
        (root / "scripts" / "tool.py").write_text(
            "# SPDX-License-Identifier: Apache-2.0\nprint('x')\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "add", "scripts/tool.py"], cwd=root, check=True)

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[header] scripts/tool.py lacks SPDX-FileCopyrightText",
            result.stdout,
        )

    def test_all_four_canonical_legal_codes_are_required(self):
        root = self.make_repo()
        (root / "LICENSES" / "CC0-1.0.txt").unlink()

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[legal-code] required LICENSES/CC0-1.0.txt is missing",
            result.stdout,
        )

    def test_exclusion_requires_reason(self):
        root = self.make_repo()
        metadata = (root / "REUSE.toml").read_text(encoding="utf-8")
        (root / "REUSE.toml").write_text(
            metadata.replace('reason = "aggregate archive validated separately"',
                             'reason = ""'),
            encoding="utf-8",
        )

        result = self.run_checker(root)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[exclusion] dist/** has no reason", result.stdout)


if __name__ == "__main__":
    unittest.main()
