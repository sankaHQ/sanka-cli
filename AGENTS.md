# Historical Sanka CLI source

This repository retains the pre-0.2 CLI and its release history. The maintained
`sanka-cli` package is owned by `sankaHQ/sanka`; the Homebrew formula is owned by
`sankaHQ/homebrew-cli`. See `docs/release.md` for verified publishing ownership.

Do not restore a publisher or add product features here. Preserve historical
release artifacts. Any remaining compatibility fixes must keep business logic
on the server and contain no credentials or customer data.

For historical-source verification:

```sh
uv sync --frozen
uv run -- python -m pytest tests/ -q
```

Workspace-wide rules apply from the parent `sanka-project` repository.
