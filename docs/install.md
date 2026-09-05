# Install

Use the maintained package from PyPI:

```sh
uv tool install --upgrade sanka-cli
sanka --version
```

For a reproducible install of the distribution verified during this cutover:

```sh
uv tool install sanka-cli==0.2.3
```

The package requires Python 3.12 or newer and includes the local migration
runtime. Add the optional MCP dependencies with `uv tool install 'sanka-cli[mcp]'`.

Homebrew users can install or upgrade from the maintained tap:

```sh
brew install sankaHQ/cli/sanka
brew upgrade sankaHQ/cli/sanka
```

The bootstrap script retained on this repository's default branch installs
0.2.3 from PyPI. Scripts and release assets under historical tags remain
historical; they are not a supported fallback for current installations.
