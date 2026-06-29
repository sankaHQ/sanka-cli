# Install

## From PyPI

This is the default install path:

```bash
uv tool install sanka-cli
```

## Bootstrap Script

```bash
curl -fsSLO https://raw.githubusercontent.com/sankaHQ/sanka-cli/v0.1.3/scripts/install.sh
sh install.sh
```

The script requires `uv` to be installed already and installs the pinned PyPI
release by default. If a fallback is needed, set `SANKA_CLI_FALLBACK_SPEC` to an
exact version or pinned Git ref, such as `sanka-cli==0.1.3` or
`git+https://github.com/sankaHQ/sanka-cli.git@v0.1.3`.

## From GitHub

Use an immutable tag, not the moving default branch:

```bash
uv tool install "git+https://github.com/sankaHQ/sanka-cli.git@v0.1.3"
```

## Homebrew

Tagged releases generate `packaging/homebrew/sanka.rb` with the exact release checksum,
and the published tap lives in [`sankaHQ/homebrew-cli`](https://github.com/sankaHQ/homebrew-cli):

```bash
brew tap sankaHQ/cli
brew install sankaHQ/cli/sanka
```

If you installed an older preview from `sankaHQ/tap`
(`sankaHQ/homebrew-tap`), remove the old formula and untap it before
installing from the new tap:

```bash
brew uninstall sanka
brew untap sankaHQ/tap
brew tap sankaHQ/cli
brew install sankaHQ/cli/sanka
```

## Local Development

```bash
uv tool install .
```
