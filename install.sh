#!/usr/bin/env bash
set -euo pipefail

SCRIPT_SOURCE="${BASH_SOURCE[0]-}"
if [[ -n "$SCRIPT_SOURCE" && -f "$SCRIPT_SOURCE" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)"
  exec "$SCRIPT_DIR/install_gptcode.sh" "$@"
fi

REPO_BASE_URL="${GPTCODE_INSTALL_REPO_URL:-https://raw.githubusercontent.com/CoYoDuDe/GPTCode/main}"
INSTALL_HELPER_URL="${REPO_BASE_URL%/}/install_gptcode.sh"

curl -fsSL "$INSTALL_HELPER_URL" | bash -s -- "$@"
