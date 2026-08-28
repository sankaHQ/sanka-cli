# Sanka CLI

Thin command-line wrapper for Sanka's public CRM and AI API.

The CLI keeps business logic on the server. It handles:
- Developer API token auth and refresh
- local profile and config management
- request construction for CRM, workflow, and AI endpoints
- table or JSON output
- polling for long-running workflow runs

## Install

From PyPI:

```bash
uv tool install sanka-cli
```

Bootstrap script from a pinned release tag:

```bash
curl -fsSLO https://raw.githubusercontent.com/sankaHQ/sanka-cli/v0.1.3/scripts/install.sh
sh install.sh
```

From a pinned GitHub release tag:

```bash
uv tool install "git+https://github.com/sankaHQ/sanka-cli.git@v0.1.3"
```

Homebrew support is published through
[`sankaHQ/homebrew-cli`](https://github.com/sankaHQ/homebrew-cli). Install with:

```bash
brew tap sankaHQ/cli
brew install sankaHQ/cli/sanka
```

If you previously installed `sanka` from the old `sankaHQ/tap` tap
(`sankaHQ/homebrew-tap`), remove that formula and untap it first:

```bash
brew uninstall sanka
brew untap sankaHQ/tap
brew tap sankaHQ/cli
brew install sankaHQ/cli/sanka
```

## Authenticate

Create a Developer API Token in Sanka, then save it locally. Login verifies the
token against the API and prints the workspace and user it belongs to; a
rejected token is not saved. If the API is unreachable, the token is saved with
a warning so offline setup still works.

```bash
sanka auth login --access-token "<ACCESS_TOKEN>"
```

## Migration commands

`sanka` also fronts the Sanka migration engine: `scan`, `plan`, `validate`,
`apply`, `verify`, `status`, `migrate`, `connect`, `research`, and `assess`
are delegated to the `sanka-migrate` package when it is available (in the same
environment or as its own tool on PATH). Install it once and the commands just
work — no API token needed for local migration runs:

```bash
uv tool install sanka-migrate
sanka scan .
```

Check the active profile:

```bash
sanka auth status
```

## Command Areas

CRM records:

```bash
sanka companies list
sanka contacts get <contact-id>
sanka deals create --data @deal.json
sanka tickets delete <ticket-id>
```

Workflow automation:

```bash
sanka workflows list
sanka workflows run <workflow-ref>
sanka workflows run <workflow-ref> --wait
```

Custom Code — write a workflow action in JavaScript or Python, keep it in your own
repository, and push versions to Sanka:

```bash
sanka code init --slug enrich-company --runtime node
sanka code create
sanka code push --activate -m "add tier logic"
```

Your repository is the source of truth. Versions are immutable and content-addressed,
so pushing unchanged code returns the version that already exists — safe to run on
every CI merge. Rolling back is a pointer move, not a redeploy:

```bash
sanka code versions enrich-company
sanka code rollback enrich-company          # or: deploy --version 4
```

`pull` writes a deployed version back to disk and `diff` reports whether your working
directory matches what is live. `diff` exits non-zero when they differ, which makes it
usable as a CI drift check:

```bash
sanka code pull enrich-company --dir ./functions/enrich
sanka code diff --dir ./functions/enrich
```

Secrets are per-function and never readable back — `list` shows only a masked suffix:

```bash
sanka code secrets set enrich-company CLEARBIT_API_KEY   # prompts, no echo
sanka code secrets list enrich-company
```

Files are excluded from a push by `.sankaignore`; `.git`, `node_modules`,
`__pycache__`, `.venv`, build output, and `.env` are excluded by default.

AI helpers:

```bash
sanka ai score company <record-id>
sanka ai score deal <record-id> --score-model-id <score-model-id>
sanka ai enrich company <record-id> --force-refresh
sanka ai enrich company --seed-name "Acme" --seed-url "https://acme.example" --dry-run
```

## Output Modes

The CLI defaults to table output on a TTY and JSON otherwise. Override this per
command when needed:

```bash
sanka --output json companies list
```

## Environment Overrides

- `SANKA_PROFILE`
- `SANKA_BASE_URL`
- `SANKA_ACCESS_TOKEN`

These override stored profile values without persisting them.

## Docs

- [Install](docs/install.md)
- [Commands](docs/commands.md)
- [Release](docs/release.md)
