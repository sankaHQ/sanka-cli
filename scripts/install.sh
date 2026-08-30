#!/usr/bin/env sh
set -eu

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required before installing sanka-cli." >&2
  echo "Install uv from Homebrew or the reviewed upstream installer, then rerun this script." >&2
  exit 1
fi

PACKAGE_SPEC="${SANKA_CLI_PACKAGE_SPEC:-sanka-cli==0.1.3}"
FALLBACK_SPEC="${SANKA_CLI_FALLBACK_SPEC:-}"

validate_fallback_spec() {
  case "$1" in
    sanka-cli==*|git+https://github.com/sankaHQ/sanka-cli.git@*) return 0 ;;
    *)
      echo "SANKA_CLI_FALLBACK_SPEC must be an exact PyPI version or a pinned Git ref." >&2
      echo "Examples: sanka-cli==0.1.3 or git+https://github.com/sankaHQ/sanka-cli.git@v0.1.3" >&2
      return 1
      ;;
  esac
}

echo "Installing sanka CLI..."
if uv tool install --upgrade "$PACKAGE_SPEC"; then
  INSTALLED_SPEC="$PACKAGE_SPEC"
elif [ -n "$FALLBACK_SPEC" ]; then
  validate_fallback_spec "$FALLBACK_SPEC"
  echo "Primary package source unavailable, using explicit pinned fallback..."
  uv tool install --upgrade "$FALLBACK_SPEC"
  INSTALLED_SPEC="$FALLBACK_SPEC"
else
  echo "Failed to install $PACKAGE_SPEC and no pinned SANKA_CLI_FALLBACK_SPEC was provided." >&2
  exit 1
fi

echo "Installed from $INSTALLED_SPEC"
echo "Run: sanka login --access-token '<ACCESS_TOKEN>'"
