# Commands

## Authentication

`login` verifies the token against the API before saving it and prints the
workspace, user, and token name on success.

```bash
sanka login --access-token "<ACCESS_TOKEN>"
sanka whoami
sanka logout
```

The nested `sanka auth login|status|logout` commands remain aliases for existing
scripts.

## Profiles

```bash
sanka profiles list
sanka profiles use prod
```

## Migration

### Sanka Cloud

Passing `--program` or `--migration` routes lifecycle commands to the hosted
Migration API:

```bash
sanka plan --program program_001
sanka apply --program program_001 --migration migration_001
sanka status --program program_001
sanka pause --migration migration_001
sanka resume --migration migration_001
sanka repair --migration migration_001
sanka verify --migration migration_001
sanka review --migration migration_001
```

`plan --program` creates the Program's first migration when needed and waits for
the reviewable plan by default. Use `--new` to create a fresh migration or
`--no-wait` to return after scheduling. `apply` binds execution to the current
plan hash and asks for confirmation unless `--yes` is supplied. A Program with
multiple migrations must be disambiguated with `--migration`.

### Local runtime

The migration lifecycle is provided by the `sanka-migrate` package; `sanka`
delegates these commands to it automatically when it is installed (same
environment, or as its own tool on PATH). No API token is required for local
migration runs.

```bash
sanka scan .
sanka plan . --to fastapi
sanka apply --to fastapi
sanka verify --to fastapi
```

Also delegated: `validate`, `test`, `status`, `migrate`, `connect`,
`research`, `assess`.

The base CLI intentionally does not bundle the engine or its providers. Install
the engine with `uv tool install sanka-migrate`; `sanka` delegates to the
`sanka-migrate` binary on PATH. The explicit command remains available for
scripts that want to name the local runtime directly.

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
