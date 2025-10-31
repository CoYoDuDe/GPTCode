# GPTCode – Nutzungshinweise

## Interaktive Nutzung (REPL)
1. Wechsle in den Projektordner:
   ```bash
   cd /dein/projekt
   ```
2. Starte GPTCode:
   ```bash
   gptcode
   ```
3. Formuliere deine Aufgaben in natürlicher Sprache.
4. Bestätige vorgeschlagene Aktionen mit `:yes` oder lehne sie mit `:no` ab.

### Wichtige REPL-Befehle
- `:help` – verfügbare Steuerbefehle anzeigen
- `:cwd` – aktuelles Arbeitsverzeichnis ausgeben
- `:cd <pfad>` – Arbeitsverzeichnis wechseln
- `:dryrun on|off` – Schreib-/Ausführaktionen nur simulieren oder freigeben
- `:auto on|off` – vorgeschlagene Schritte automatisch genehmigen oder stoppen
- `:quit` – Sitzung beenden

## Headless-Automatisierung
Der Headless-Modus eignet sich für reproduzierbare Automatisierungen. GPTCode verarbeitet dabei eine Zielbeschreibung ohne weitere Rückfragen.

```bash
gptcode --headless --goal "Analysiere, teste und finalisiere dieses Projekt (systemd, Nginx, Docker, PyTest)."
```

Empfehlungen:
- Verwende `--headless` nur in isolierten Test- oder Staging-Umgebungen.
- Hinterlege `--goal` präzise, inkl. Tests, Deployments und Freigabeprozesse.
- Überwache Log-Ausgaben (z. B. via `--log-file`), um Eingriffe bei Bedarf einleiten zu können.

## Konfigurationspfad
Beim ersten Start fragt GPTCode nach OpenAI-Zugangsdaten und speichert sie in:
```
~/.config/gptcode/config.json
```

## Automatisierungsfunktionen
- **Werkzeugkasten** (nach Bestätigung): `list_dir`, `read_file`, `write_file`, `apply_patch`, `run`
- **Analyse- und Service-Tools**: `tail_file`, `systemctl`, `docker` (inkl. Compose), `pytest`
- **Sicherheitsoptionen**: `:dryrun` für Trockenläufe, `:auto` für automatische Freigaben

## Weitere Hilfe
Vertiefende Beispiele findest du im Abschnitt „Beispiele“ der README sowie im `CHANGELOG.md` für historische Workflows.
