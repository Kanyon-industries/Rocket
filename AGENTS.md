# AGENTS.md

## Repository Scope
This repository hosts public documentation, release links, and resources for rocket engine research and development by Kanyon Industries and Lunapolis Dynamics, including the Rocket Designer System software and the AWSL-01 Rocket Engine Test Stand System.

## Safe Change Rules
- Do not modify or delete the technical documentation content or release links in `README.md`, `eng-README.md`, `jp-README.md`, or `LICENSE`.
- Keep modifications minimal, safe, and focused strictly on the requested task.
- Ensure all local file references and Markdown links point to valid targets within the repository.
- Avoid introducing any broken references or path escapes.

## Required Validation
Before submitting any changes:
1. Run documentation validation:
   ```bash
   py scripts/validate_docs.py
   ```
2. Run test suites:
   ```bash
   py -m unittest discover -s tests -v
   ```
All validation checks and unit tests must exit with status code 0.

## Branching and PR Policy (No Direct Main Edits)
- Direct commits and pushes to the `main` branch are prohibited.
- All contributions and automated agent changes must be prepared on a dedicated branch and submitted through a Pull Request.
- Continuous integration checks (`docs-integrity.yml`) must pass prior to merge.
