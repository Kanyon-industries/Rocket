#!/usr/bin/env python3
"""Unit tests for scripts/validate_docs.py."""

from __future__ import annotations

import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import validate_docs


class TestValidateDocs(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name).resolve()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _create_valid_structure(self) -> None:
        (self.root / "README.md").write_text(
            "# Title\n\n[Doc](eng-README.md)\n", encoding="utf-8"
        )
        (self.root / "eng-README.md").write_text(
            "# English\n\n[JP](jp-README.md)\n", encoding="utf-8"
        )
        (self.root / "jp-README.md").write_text(
            "# Japanese\n\n[Home](README.md)\n", encoding="utf-8"
        )

    def test_positive_valid_repository(self) -> None:
        self._create_valid_structure()
        errors = validate_docs.validate_repository(self.root)
        self.assertEqual(errors, [])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(validate_docs.main([str(self.root)]), 0)

    def test_negative_missing_readme(self) -> None:
        self._create_valid_structure()
        (self.root / "eng-README.md").unlink()

        errors = validate_docs.validate_repository(self.root)
        self.assertTrue(
            any("eng-README.md' does not exist" in err for err in errors),
            f"Expected missing readme error, got {errors}",
        )
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertNotEqual(validate_docs.main([str(self.root)]), 0)

    def test_negative_empty_readme(self) -> None:
        self._create_valid_structure()
        (self.root / "jp-README.md").write_text("   \n\t\n", encoding="utf-8")

        errors = validate_docs.validate_repository(self.root)
        self.assertTrue(
            any("jp-README.md' is empty" in err for err in errors),
            f"Expected empty readme error, got {errors}",
        )
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertNotEqual(validate_docs.main([str(self.root)]), 0)

    def test_positive_ignored_links(self) -> None:
        self._create_valid_structure()
        (self.root / "README.md").write_text(
            "# Links\n\n"
            "[External](https://example.com)\n"
            "[Insecure](http://example.com/test)\n"
            "[Mail](mailto:test@example.com)\n"
            "[Section](#heading)\n"
            "[Image](https://example.com/logo.png)\n"
            "[Target With Title](README.md \"Title\")\n",
            encoding="utf-8",
        )
        errors = validate_docs.validate_repository(self.root)
        self.assertEqual(errors, [])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(validate_docs.main([str(self.root)]), 0)

    def test_negative_broken_link(self) -> None:
        self._create_valid_structure()
        (self.root / "README.md").write_text(
            "# Bad Link\n\n[Missing File](does_not_exist.md)\n",
            encoding="utf-8",
        )
        errors = validate_docs.validate_repository(self.root)
        self.assertTrue(
            any("does_not_exist.md" in err and "does not exist" in err for err in errors),
            f"Expected broken link error, got {errors}",
        )
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertNotEqual(validate_docs.main([str(self.root)]), 0)

    def test_negative_path_escaping_repository(self) -> None:
        self._create_valid_structure()
        (self.root / "README.md").write_text(
            "# Escape Link\n\n[Escape](../../outside.txt)\n",
            encoding="utf-8",
        )
        errors = validate_docs.validate_repository(self.root)
        self.assertTrue(
            any("escapes the repository" in err for err in errors),
            f"Expected escape error, got {errors}",
        )
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertNotEqual(validate_docs.main([str(self.root)]), 0)

    def test_positive_nested_links_and_anchors(self) -> None:
        self._create_valid_structure()
        sub_dir = self.root / "docs" / "sub"
        sub_dir.mkdir(parents=True)
        target = sub_dir / "target.md"
        target.write_text("# Target\n", encoding="utf-8")

        (self.root / "README.md").write_text(
            "# Root\n\n[Sub Target](docs/sub/target.md#section?foo=bar)\n",
            encoding="utf-8",
        )
        errors = validate_docs.validate_repository(self.root)
        self.assertEqual(errors, [])

    def test_reference_style_links(self) -> None:
        self._create_valid_structure()
        (self.root / "README.md").write_text(
            "# Ref Links\n\n[Valid][1]\n[Broken][2]\n\n"
            "[1]: eng-README.md\n"
            "[2]: non_existent.txt\n",
            encoding="utf-8",
        )
        errors = validate_docs.validate_repository(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("non_existent.txt", errors[0])

    def test_main_cli_output(self) -> None:
        self._create_valid_structure()
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        orig_stdout, orig_stderr = sys.stdout, sys.stderr
        try:
            sys.stdout = stdout_buf
            sys.stderr = stderr_buf
            code = validate_docs.main([str(self.root)])
            self.assertEqual(code, 0)
            self.assertIn("Documentation validation passed successfully", stdout_buf.getvalue())
        finally:
            sys.stdout, sys.stderr = orig_stdout, orig_stderr


if __name__ == "__main__":
    unittest.main()
