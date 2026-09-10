#!/usr/bin/env python3
"""Validation script for repository documentation and Markdown link targets.

Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import urllib.parse

REQUIRED_READMES = ("README.md", "eng-README.md", "jp-README.md")
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[([^\]]*)\]\(((?:[^()]+|\([^()]*\))*)\)")
REFERENCE_LINK_PATTERN = re.compile(r"^\s*\[([^\]]+)\]:\s*(<[^>]+>|\S+)", re.MULTILINE)


def is_ignored_url(url: str) -> bool:
    """Return True if URL is empty, fragment-only, or an external scheme."""
    clean = url.strip()
    if not clean or clean.startswith("#"):
        return True
    lower = clean.lower()
    return lower.startswith(("http://", "https://", "mailto:"))


def extract_link_target(raw_target: str) -> str:
    """Extract clean link target by stripping angle brackets and titles."""
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.find(">")].strip()
    else:
        for quote in ('"', "'"):
            if quote in target:
                target = target.split(quote, 1)[0].strip()
        parts = target.split()
        target = parts[0] if parts else ""
    return target


def extract_markdown_links(content: str) -> list[str]:
    """Extract all inline and reference Markdown link targets from content."""
    links: list[str] = []
    for match in MARKDOWN_LINK_PATTERN.finditer(content):
        target = extract_link_target(match.group(2))
        links.append(target)
    for match in REFERENCE_LINK_PATTERN.finditer(content):
        target = extract_link_target(match.group(2))
        links.append(target)
    return links


def is_path_escaping_repo(target_path: Path, repo_root: Path) -> bool:
    """Return True if target_path resolves outside the repo_root boundary."""
    try:
        resolved_target = target_path.resolve()
        resolved_repo = repo_root.resolve()
        return not resolved_target.is_relative_to(resolved_repo)
    except (ValueError, RuntimeError):
        return True


def resolve_link_target(link: str, source_file: Path, repo_root: Path) -> Path:
    """Resolve a repository-local link target relative to source file or repo root."""
    target_path_str = link.split("#", 1)[0].split("?", 1)[0].strip()
    target_path_str = urllib.parse.unquote(target_path_str)

    if target_path_str.startswith(("/", "\\")):
        return repo_root / target_path_str.lstrip("/\\")

    candidate = Path(target_path_str)
    if candidate.is_absolute():
        return candidate

    return source_file.parent / target_path_str


def validate_required_readmes(repo_root: Path) -> list[str]:
    """Validate that README.md, eng-README.md, and jp-README.md exist and are non-empty."""
    errors: list[str] = []
    for filename in REQUIRED_READMES:
        file_path = repo_root / filename
        if not file_path.exists():
            errors.append(f"Required file '{filename}' does not exist.")
        elif not file_path.is_file():
            errors.append(f"Required path '{filename}' is not a file.")
        else:
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                if file_path.stat().st_size == 0 or not content.strip():
                    errors.append(f"Required file '{filename}' is empty.")
            except OSError as e:
                errors.append(f"Could not read required file '{filename}': {e}")
    return errors


def validate_markdown_links(repo_root: Path) -> list[str]:
    """Validate repository-local Markdown link targets in all .md files."""
    errors: list[str] = []
    ignored_parts = {".git", ".venv", "node_modules"}

    md_files = [
        p
        for p in repo_root.rglob("*.md")
        if not any(part in ignored_parts for part in p.parts)
    ]

    for md_file in sorted(md_files):
        rel_source = md_file.relative_to(repo_root)
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            errors.append(f"Failed to read '{rel_source}': {e}")
            continue

        links = extract_markdown_links(content)
        for link in links:
            if is_ignored_url(link):
                continue

            target_path_str = link.split("#", 1)[0].split("?", 1)[0].strip()
            target_path_str = urllib.parse.unquote(target_path_str)
            if not target_path_str:
                continue

            target_path = resolve_link_target(link, md_file, repo_root)

            if is_path_escaping_repo(target_path, repo_root):
                errors.append(
                    f"Link target '{link}' in '{rel_source}' escapes the repository."
                )
            elif not target_path.resolve().exists():
                errors.append(
                    f"Link target '{link}' in '{rel_source}' does not exist."
                )

    return errors


def validate_repository(repo_root: Path | str | None = None) -> list[str]:
    """Validate required README files and local Markdown link targets."""
    root = Path.cwd() if repo_root is None else Path(repo_root)
    root = root.resolve()

    errors: list[str] = []
    errors.extend(validate_required_readmes(root))
    errors.extend(validate_markdown_links(root))
    return errors


def main(argv: list[str] | None = None) -> int:
    """CLI entry point for docs validation."""
    parser = argparse.ArgumentParser(
        description="Validate repository documentation and Markdown links."
    )
    parser.add_argument(
        "repo_path",
        nargs="?",
        default=".",
        help="Path to repository root (defaults to current working directory)",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_path).resolve()
    errors = validate_repository(repo_root)

    if errors:
        print(
            f"Documentation validation failed with {len(errors)} error(s):",
            file=sys.stderr,
        )
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Documentation validation passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
