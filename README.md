# Sanka CLI

Thin command-line wrapper for Sanka's public CRM and AI API.

The CLI keeps business logic on the server. It handles:
- Developer API token auth and refresh
- local profile and config management
- request construction for CRM, workflow, and AI endpoints
- table or JSON output
- polling for long-running workflow runs

## Install

From GitHub:

```bash
uv tool install "git+https://github.com/sankaHQ/sanka-cli.git"
```

Bootstrap script:

```bash
curl -fsSL https://raw.githubusercontent.com/sankaHQ/sanka-cli/main/scripts/install.sh | sh
```

From PyPI after the first package release:

```bash
uv tool install sanka-cli
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

Create a Developer API Token in Sanka, then save it locally:

```bash
sanka auth login --access-token "<ACCESS_TOKEN>"
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
