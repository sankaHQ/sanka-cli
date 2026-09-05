# Publishing ownership

`sanka-cli` 0.2.3 and later are published by `sankaHQ/sanka` through `publish.yml`
and its protected `pypi` environment. Verify this against the package's
[PyPI provenance](https://pypi.org/integrity/sanka-cli/0.2.3/sanka_cli-0.2.3.tar.gz/provenance).

This repository must not publish new Python packages or Homebrew release assets.
The old release workflow and formula generator have been removed. Historical
GitHub release artifacts remain available for reproducibility.

The [Homebrew tap](https://github.com/sankaHQ/homebrew-cli) pins the PyPI source
archive and checksum and owns its formula.

Before archiving this repository, merge and verify the Homebrew cutover and
remove the old PyPI trusted publisher tuple (`sankaHQ/sanka-cli`, `release.yml`,
`pypi`) from the project's publishing settings. Retain the current publisher
(`sankaHQ/sanka`, `publish.yml`, `pypi`). Removing a workflow from the default
branch alone does not revoke the trust granted to historical refs.
