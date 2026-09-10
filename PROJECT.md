# Project Overview

This repository hosts public documentation, release links, and technical resources for rocket engine research and development by Kanyon Industries and Lunapolis Dynamics, including the Rocket Designer System software and the AWSL-01 Rocket Engine Test Stand System.

## Documentation Entry Points

The primary documentation is available in three languages:

- [README](README.md) (Chinese / 中文)
- [English](eng-README.md) (English)
- [Japanese](jp-README.md) (Japanese / 日本語)

Additional repository references:
- [License](LICENSE) - GNU Affero General Public License v3.0
- [Agent Guidelines](AGENTS.md) - Operational guidelines and safe change rules

## Testing and Validation Commands

To validate documentation links, ensure non-empty required files, and run the test suite, use the following commands:

- Run documentation validator:
  ```bash
  python scripts/validate_docs.py
  ```
  *(On Windows with Python Launcher, `py scripts/validate_docs.py` may also be used.)*

- Run unit tests:
  ```bash
  python -m unittest discover -s tests -v
  ```
  *(On Windows with Python Launcher, `py -m unittest discover -s tests -v` may also be used.)*

All validation scripts and unit test suites must exit with status code 0.

## CI Workflow

Continuous integration is automated via GitHub Actions:
- Workflow file: [.github/workflows/docs-integrity.yml](.github/workflows/docs-integrity.yml)
- Triggers: Push and pull request events targeting the `main` branch.
- Checks executed:
  1. Check out repository
  2. Set up Python environment
  3. Validate documentation via `python scripts/validate_docs.py`
  4. Execute test suite via `python -m unittest discover -s tests -v`

All CI checks must pass prior to merging any pull request.

## Branching and Pull Request Rules

- **No Direct Main Edits**: Direct commits and pushes to the `main` branch are strictly prohibited.
- **Dedicated Branches**: All changes and automated agent updates must be developed on a dedicated branch.
- **Pull Request Required**: Contributions must be submitted via a Pull Request against `main`.
- **Integrity Verification**: Pull Requests must pass all CI checks (`docs-integrity.yml`) and adhere to the safe change policy defined in [AGENTS.md](AGENTS.md).
