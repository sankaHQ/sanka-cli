# sanka-cli Agent Guide

Canonical agent instructions for this repo — `CLAUDE.md` symlinks here. Workspace-wide
rules and the repo map live in the sanka-project workspace repo (`../AGENTS.md`).

## What this is

Public command-line interface for Sanka — a thin wrapper over the public CRM and AI
API. Business logic stays on the server; the CLI handles developer API token auth and
refresh, local profile/config management, request construction, table/JSON output, and
polling for long-running workflow runs.

## Stack & layout

- Python ≥3.11, click + httpx + rich; keyring for token storage, platformdirs for config paths.
- Package `sanka_cli/`, tests in `tests/`, packaging assets in `packaging/`, install script at `scripts/install.sh`.
- Published to PyPI as `sanka-cli`; installable via `uv tool install sanka-cli` or the bootstrap script.

## Commands

```bash
uv sync
uv run -- python -m pytest tests/ -q
uv run sanka --help
```

## Release flow

1. Bump `version` in `pyproject.toml`, tag and create a GitHub Release with the sdist (`sanka_cli-<ver>.tar.gz`).
2. Update the Homebrew tap: `../homebrew-cli/Formula/sanka.rb` pins the release `url` + `sha256` (plus vendored resource blocks) — it must be updated after every release or `brew install sankaHQ/cli/sanka` ships the old version.

## Gotchas

- Keep it thin: if a feature needs business logic, it belongs in the server API, not here.
- This repo is public — no internal URLs, workspace paths, or credentials in code, docs, or fixtures.
