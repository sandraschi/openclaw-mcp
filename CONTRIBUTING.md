# Contributing to openclaw-mcp

## Setup

1. Clone the repo and go to the repo root.
2. Install dependencies: `.\scripts\install.ps1` (or `scripts\install.bat`).
3. Run checks: `.\scripts\check.ps1` or, if you use [just](https://github.com/casey/just), `just check`.

## Before submitting

- Run lint/format: `ruff check src tests --fix` and `ruff format src tests`.
- Run typecheck: `mypy src`.
- Run tests: `pytest tests -v`.
- Pre-commit is configured (`.pre-commit-config.yaml`); run `pre-commit run --all-files` if you use it.

## Pull requests

- Open a branch, make changes, push, open a PR against `main` (or the default branch).
- Keep PRs focused. Link any related issues.
- Maintainers will review and may ask for changes.

## Code style

- Python: ruff (line length 100), type hints, mypy-clean.
- No Unicode emojis in source or logger messages (see repo rules).
- Use pathlib and cross-platform patterns where relevant.

## Docs

- Update README.md, INSTALL.md, or docs under `docs/` if behavior or setup changes.
- CHANGELOG.md: add a short entry for user-visible changes.

## Security

- Do not commit secrets or credentials. See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.
