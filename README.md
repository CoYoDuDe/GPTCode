# GPTCode — Chat‑first DevOps/Coding Assistant (Claude‑Style, Terminal)

**GPTCode** ist ein interaktiver Terminal‑Assistent, der wie „Claude Code“ arbeitet:
Du startest ihn im Projektordner, chattest natürlich, und er kann – nach deiner Bestätigung –
Dateien **lesen/schreiben**, **Patches anwenden**, **Befehle ausführen**, **Logs anzeigen**,
**systemd** steuern, **Docker Compose** bedienen und **Tests** mit `pytest` ausführen.
Außerdem gibt es einen **Auto/Headless‑Modus** (“finalisieren”).

## Features
- Chat‑REPL: natürliche Eingaben, kein starres CLI nötig
- Werkzeugkasten (nach Bestätigung): `list_dir`, `read_file`, `write_file`, `apply_patch`, `run`
- Extra‑Tools: `tail_file` (Logs), `systemctl`, `docker` (compose), `pytest`
- **:dryrun on/off** für sichere Trockenläufe
- **:auto on/off** für automatische Schrittfreigabe
- **Headless**: `--headless --goal "…"`, um eine Finalisierungs‑Pipeline auszuführen
- First‑Run‑Wizard: fragt nach API‑Key & Modell, speichert in `~/.config/gptcode/config.json`

## Installation
```bash
sudo bash install_gptcode.sh
```

## Nutzung
```bash
cd /dein/projekt
gptcode
# you> Analysiere das Projekt, härte nginx, schreibe systemd unit, führe Tests aus.
# Bestätige Aktionen mit :yes (oder lehne ab mit :no)
```

### Nützliche REPL‑Befehle
- `:help` – Hilfe
- `:cwd` – Ordner anzeigen
- `:cd <pfad>` – wechseln
- `:dryrun on|off` – Schreib/Ausführ‑Dry‑Run
- `:auto on|off` – Schritte automatisch erlauben
- `:quit` – beenden

### Headless‑Modus (vorsichtig verwenden)
```bash
gptcode --headless --goal "Analysiere, teste und finalisiere dieses Projekt (systemd, Nginx, Docker, PyTest)."
```

## Voraussetzungen
- Debian/Ubuntu mit `python3`, `python3-venv`, `python3-pip`
- OpenAI API‑Key (wird beim ersten Start abgefragt)
- Optional: `docker` + `docker compose` (für Docker‑Projekte), `pytest` (für Tests)

## Lizenz
MIT
