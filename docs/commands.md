# Commands

## Authentication

`auth login` verifies the token against the API before saving it and prints the
workspace, user, and token name on success.

```bash
sanka auth login --access-token "<ACCESS_TOKEN>"
sanka auth status
sanka auth logout
```

## Profiles

```bash
sanka profiles list
sanka profiles use prod
```

## Migration (delegated to sanka-migrate)

The migration lifecycle is provided by the `sanka-migrate` package; `sanka`
delegates these commands to it automatically when it is installed (same
environment, or as its own tool on PATH). No API token is required for local
migration runs.

```bash
uv tool install sanka-migrate   # once
sanka scan .
sanka plan . --to fastapi
sanka apply --to fastapi
sanka verify --to fastapi
```

Also delegated: `validate`, `status`, `migrate`, `connect`, `research`,
`assess`.

Both packages currently ship a `sanka` script, so install them as separate
tools, in one of two orders:

- **Homebrew CLI** (recommended): `brew install sankaHQ/cli/sanka`, then
  `uv tool install sanka-migrate`. Keep Homebrew's bin ahead of `~/.local/bin`
  in PATH.
- **uv only**: `uv tool install sanka-migrate` first, then
  `uv tool install sanka-cli --force` (sanka-cli takes the `sanka` name;
  delegation finds sanka-migrate via its own alias).

Do not install both into one shared virtualenv — the last install wins the
`sanka` script.

## CRM

```bash
sanka companies list
sanka companies get <company-id>
sanka contacts get <contact-id>
sanka deals create --data @deal.json
sanka tickets delete <ticket-id>
```

## Workflows

```bash
sanka workflows list
sanka workflows get <workflow-ref>
sanka workflows run <workflow-ref> --wait
```

## AI

```bash
sanka ai score company <record-id>
sanka ai score deal <record-id> --score-model-id <score-model-id>
sanka ai enrich company <record-id> --force-refresh
sanka ai enrich company --seed-name "Acme" --seed-url "https://acme.example" --dry-run
```

## Output

```bash
sanka --output json companies list
```
