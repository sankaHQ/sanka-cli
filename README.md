# Sanka CLI (historical source)

The maintained `sanka-cli` distribution is published from `sankaHQ/sanka`.
This repository retains the pre-0.2 source and release history; it no longer
publishes Python packages or generates the Homebrew formula.

Install the current package from [PyPI](https://pypi.org/project/sanka-cli/):

```sh
uv tool install --upgrade sanka-cli
```

Or use the [Homebrew tap](https://github.com/sankaHQ/homebrew-cli):

```sh
brew install sankaHQ/cli/sanka
```

The current package includes both hosted API commands and the local migration
runtime. Do not install an old Git tag from this repository for current use.

See [installation](docs/install.md) and [publishing ownership](docs/release.md).
