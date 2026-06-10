# Commands

## Authentication

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
