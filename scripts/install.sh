#!/usr/bin/env sh
set -eu

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required before installing sanka-cli." >&2
  echo "Install uv, then rerun this script." >&2
  exit 1
fi

# Compatibility entrypoint: releases are now owned by sankaHQ/sanka.
exec uv tool install --upgrade sanka-cli==0.2.3
