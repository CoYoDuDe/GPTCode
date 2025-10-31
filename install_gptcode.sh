#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo "GPTCode Installer – Hinweise zur sicheren Installation"
echo "============================================================"
cat <<'INFO'
• Diese Installation folgt PEP 668 (Externally Managed Environments).
  Verwenden Sie nach Möglichkeit eine isolierte Umgebung (python3 -m venv) oder pipx.
• Systemweite Python-Pakete werden nur ergänzt, bestehende Venvs bleiben unverändert.
• Abbruch mit STRG+C, falls Sie zunächst ein Backup oder eine eigene venv anlegen möchten.
INFO

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFIX="/usr/local"
BIN_DIR="$PREFIX/bin"
APP_DIR="/opt/gptcode"
VENV_DIR="$APP_DIR/venv"

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Bitte als root (oder mit sudo) ausführen." >&2
  exit 1
fi

missing=0

if ! command -v git >/dev/null 2>&1; then
  echo "[HINWEIS] git wurde nicht gefunden und wird über apt-get installiert." >&2
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[FEHLT] 'docker' wurde nicht gefunden. Installationshinweis: https://docs.docker.com/engine/install/" >&2
  missing=1
else
  if ! docker compose version >/dev/null 2>&1; then
    if command -v docker-compose >/dev/null 2>&1; then
      echo "[HINWEIS] docker compose (Plugin) nicht gefunden, verwende vorhandenes docker-compose Binary." >&2
    else
      echo "[FEHLT] 'docker compose' nicht verfügbar. Installationshinweis: https://docs.docker.com/compose/install/" >&2
      missing=1
    fi
  fi
fi

if ! command -v pytest >/dev/null 2>&1; then
  echo "[HINWEIS] pytest nicht gefunden. Optional via 'pipx install pytest' oder innerhalb eines venv installieren." >&2
fi

if (( missing )); then
  echo "Bitte installieren Sie die fehlenden Abhängigkeiten und starten Sie den Installer erneut." >&2
  exit 1
fi

apt-get update -y
apt-get install -y python3 python3-venv python3-pip git ca-certificates

mkdir -p "$APP_DIR" "$BIN_DIR"

backup_file() {
  local target="$1"
  if [[ -e "$target" ]]; then
    local ts
    ts=$(date +%Y%m%d_%H%M%S)
    local backup="${target}.bak.${ts}"
    cp -a "$target" "$backup"
    echo "[Backup] Bestehende Datei gesichert nach $backup"
  fi
}

target_user="${SUDO_USER:-root}"
if [[ -n "$target_user" ]]; then
  user_home=$(eval echo "~$target_user")
  user_config="$user_home/.config/gptcode/config.json"
  if [[ -f "$user_config" ]]; then
    backup_file "$user_config"
  fi
fi

if [[ -d "$VENV_DIR" ]]; then
  backup_file "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV_DIR/bin/pip" install --upgrade "$SCRIPT_DIR"

wrapper="$BIN_DIR/gptcode"
backup_file "$wrapper"
cat > "$wrapper" <<'SH'
#!/usr/bin/env bash
exec /opt/gptcode/venv/bin/python -m gptcode "$@"
SH
chmod +x "$wrapper"

echo "\n✅ GPTCode wurde erfolgreich in $VENV_DIR installiert."
echo "Start: gptcode"
echo "Konfiguration: ~/.config/gptcode/config.json"
