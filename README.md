# GPTCode — Chat‑first DevOps/Coding Assistant (Claude‑Style, Terminal)

**GPTCode** ist ein interaktiver Terminal‑Assistent für DevOps‑ und Coding‑Workflows. Er kombiniert natürliche Sprache mit kontrollierten Automatisierungen und kann — nach deiner Freigabe — Dateien lesen/schreiben, Patches anwenden, Befehle ausführen, Logs analysieren, systemd steuern, Docker Compose bedienen und Tests über `pytest` anstoßen. Ein Headless-Modus erlaubt vollautomatische Finalisierungen.

## Inhaltsverzeichnis
1. [Features](#features)
2. [Quickstart](#quickstart)
3. [Headless-Betrieb](#headless-betrieb)
4. [Beispiele](#beispiele)
5. [Weiterführende Nutzung](#weiterführende-nutzung)
6. [Troubleshooting](#troubleshooting)
7. [Weitere Dokumente](#weitere-dokumente)
8. [Lizenz](#lizenz)

## Features
- **Chat-REPL**: natürliche Eingaben statt starrem CLI.
- **Bestätigte Automatisierung**: Werkzeugkasten (`list_dir`, `read_file`, `write_file`, `apply_patch`, `run`) und Zusatztools (`tail_file`, `systemctl`, `docker`, `pytest`).
- **Sicherheitsoptionen**: `:dryrun` für Trockenläufe, `:auto` für automatische Schrittfreigabe.
- **Session-Overrides**: CLI-Flags `--model` und `--dryrun on|off` überschreiben Werte nur für die laufende Sitzung.
- **Headless-Pipeline**: `--headless --goal "…"` zur unbeaufsichtigten Finalisierung.
- **First-Run-Wizard**: fragt nach API-Key & Modell, speichert Konfiguration unter `~/.config/gptcode/config.json`.

## Quickstart
### Voraussetzungen
- Debian/Ubuntu mit `python3`, `python3-venv`, `python3-pip`.
- OpenAI API-Key (wird beim ersten Start abgefragt).
- Optional: `docker` + `docker compose` für Container-Workloads (automatische Fallbacks auf ein vorhandenes `docker-compose`-Binary sind integriert). Fehlen die Binaries, deaktiviert GPTCode die Docker-Funktionen und weist beim Start darauf hin.
- Optional: `pytest` für automatisierte Testläufe.

### Voraussetzungen prüfen
Beim Start führt GPTCode einen schnellen Werkzeug-Check durch und beendet sich nur dann mit einer Fehlermeldung, wenn `git` im `PATH` fehlt.
Optionale Tools erzeugen Hinweiszeilen: Fehlen `docker`/`docker compose`, bleiben alle Docker-Kommandos deaktiviert, bis ein Binary nachinstalliert wurde; GPTCode greift weiterhin automatisch auf ein vorhandenes Legacy-`docker-compose` zurück, sobald es verfügbar ist. Für `pytest` erscheint eine optionale Erinnerung, bevor Testläufe angefordert werden.
Nutze die Hinweise im Fehlertext (z. B. `sudo apt install git` oder die offiziellen Docker-/pytest-Dokumentationen), um fehlende Pakete nachzurüsten.

### Installation
#### Über `pipx` (empfohlen)
```bash
pipx install .
```

#### Virtuelle Umgebung + `pip`
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

#### Systemweiter Installer (legt isoliertes venv unter `/opt/gptcode` an)
Das Wrapper-Skript [`install.sh`](./install.sh) prüft automatisch, ob es aus einem echten Dateipfad oder via Pipe/`STDIN` aufgerufen wurde.
- **Remote-Aufruf**: Bei `curl … | bash` oder `bash <(curl …)` lädt es transparent die aktuelle [`install_gptcode.sh`](./install_gptcode.sh) aus dem Repository (Standard: `main`-Branch via `https://raw.githubusercontent.com/CoYoDuDe/GPTCode/main`).
- **Lokaler Aufruf**: Liegt das Repository bereits auf der Platte, wird die mitgelieferte `install_gptcode.sh` direkt gestartet.

Optional lässt sich die Quelle über `GPTCODE_INSTALL_REPO_URL=<eigene-URL>` überschreiben (z. B. für Forks oder gepinnte Releases).

```bash
curl -fsSL https://raw.githubusercontent.com/CoYoDuDe/GPTCode/main/install.sh | sudo bash
```

```bash
sudo bash install_gptcode.sh
```

#### Paket bauen (Wheel/Sdist)
```bash
pip install --upgrade build
python -m build
```

### Erstes Projekt starten
```bash
cd /dein/projekt
gptcode
```
Formuliere deine Aufgaben in natürlicher Sprache und bestätige vorgeschlagene Aktionen mit `:yes` (oder lehne mit `:no` ab). Eine Übersicht aller REPL-Befehle findest du in [USAGE.md](./USAGE.md).

#### Temporäre Overrides (optional)
```bash
gptcode --model gpt-4o --dryrun on
```
- `--model <name>`: setzt das OpenAI-Modell nur für die aktuelle Session.
- `--dryrun on|off`: aktiviert/deaktiviert Trockenlauf ohne die gespeicherte Konfiguration zu verändern.

## Headless-Betrieb
Nutze den Headless-Modus für reproduzierbare Automatisierungen ohne Rückfragen. Hinterlege dazu ein klares Ziel inklusive Prüf- und Freigabeschritten:

```bash
gptcode --headless --goal "Analysiere, teste und finalisiere dieses Projekt (systemd, Nginx, Docker, PyTest)."
```

Weitere Headless-Flags lassen sich mit Overrides kombinieren, z. B. `gptcode --headless --goal "…" --model gpt-4o-mini --dryrun off` für ein explizites Modell und reale Ausführung.

Empfehlungen:
- Nur in isolierten Test- oder Staging-Umgebungen einsetzen.
- Log-Ausgabe (z. B. via `--log-file`) überwachen, um bei Bedarf eingreifen zu können.
- Goals klar formulieren, inkl. Tests, Deployments und Rollback-Strategien.

## Beispiele
- **System-Härtung**: „Analysiere das Projekt, härte nginx, schreibe systemd unit, führe Tests aus.“
- **Container-Workflow**: „Baue das Docker-Compose-Setup, aktualisiere Images und führe Smoke-Tests aus.“
- **Release-Vorbereitung**: „Passe Changelogs an, incrementiere Version und starte Integrationstests.“

Weitere Ablauf- und REPL-Details findest du in [USAGE.md](./USAGE.md).

## Weiterführende Nutzung
Für strukturierte Schritt-für-Schritt-Anleitungen, REPL-Referenzen sowie automatisierte Headless- und Auto-Beispiele lies [USAGE.md](./USAGE.md). Dort sind praxisnahe Workflows für `systemctl`, `docker compose` und `pytest` dokumentiert.

## Troubleshooting
### Docker-Unterstützung deaktiviert
Beim Start ohne `docker` oder `docker-compose` zeigt GPTCode den Hinweis `Docker-Funktionen bleiben deaktiviert, bis `docker` oder `docker-compose` installiert und ausführbar ist`. Installiere die Docker Engine inklusive Compose Plugin ([docs.docker.com/engine/install](https://docs.docker.com/engine/install/)) oder ein Legacy-`docker-compose`-Binary und starte GPTCode anschließend erneut. Sobald ein Binary verfügbar ist, stehen die Compose-Werkzeuge wieder zur Verfügung.

### `externally-managed-environment` (PEP 668)
Wenn `pip` den Fehler `externally-managed-environment` meldet, befindet sich dein System-Python unter Paketmanager-Kontrolle (PEP 668). Zwei bewährte Lösungen:

1. **Virtuelle Umgebung nutzen**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install gptcode
   ```
2. **Isolierte Installation mit `pipx`**
   ```bash
   sudo apt install pipx
   pipx ensurepath
   pipx install gptcode
   ```

Beide Varianten halten das System-Python unverändert und bleiben konform zu PEP 668.

## Weitere Dokumente
- Aktuelle Versionsnummer: siehe [`VERSION`](./VERSION).
- Ausführliche Nutzungsszenarien: [`USAGE.md`](./USAGE.md).
- Detaillierte Änderungsübersicht nach „Keep a Changelog“: [`CHANGELOG.md`](./CHANGELOG.md).

## Lizenz
MIT
