#!/usr/bin/env bash
set -euo pipefail

SCRIPT_SOURCE="${BASH_SOURCE[0]:-}"
if [[ -n "$SCRIPT_SOURCE" && -f "$SCRIPT_SOURCE" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)"
  LOCAL_INSTALLER="$SCRIPT_DIR/install_gptcode.sh"
  if [[ -f "$LOCAL_INSTALLER" ]]; then
    exec "$LOCAL_INSTALLER" "$@"
  fi
fi

INSTALLER_URL="https://raw.githubusercontent.com/CoYoDuDe/GPTCode/main/install_gptcode.sh"
TMP_DIR="$(mktemp -d)"
trap '[[ -d "$TMP_DIR" ]] && rm -rf "$TMP_DIR"' EXIT
TMP_INSTALLER="$TMP_DIR/install_gptcode.sh"

download_installer() {
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$INSTALLER_URL" -o "$TMP_INSTALLER"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO "$TMP_INSTALLER" "$INSTALLER_URL"
  else
    echo "Error: neither curl nor wget is available to download install_gptcode.sh" >&2
    return 1
  fi
}

download_installer
chmod +x "$TMP_INSTALLER"
exec "$TMP_INSTALLER" "$@"
