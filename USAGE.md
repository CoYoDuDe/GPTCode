# GPTCode – Nutzungs- und Workflow-Guide

## Inhaltsverzeichnis
1. [Schnellreferenz der REPL-Befehle](#schnellreferenz-der-repl-befehle)
2. [Interaktive Nutzung](#interaktive-nutzung)
3. [Headless- & Auto-Betrieb](#headless--auto-betrieb)
4. [Praxis-Workflows](#praxis-workflows)
   1. [Systemdienste mit `systemctl`](#systemdienste-mit-systemctl)
   2. [Container-Stacks mit `docker compose`](#container-stacks-mit-docker-compose)
   3. [Testautomation mit `pytest`](#testautomation-mit-pytest)
5. [Konfiguration & Speicherorte](#konfiguration--speicherorte)
6. [Weiterführende Ressourcen](#weiterführende-ressourcen)

## Schnellreferenz der REPL-Befehle
| Befehl | Beschreibung | Typische Verwendung |
| --- | --- | --- |
| `:help` | Listet alle verfügbaren Steuerbefehle in der aktuellen Sitzung. | Einstieg in neue Umgebung, Nachschlagen seltener Optionen. |
| `:cwd` | Gibt das aktuelle Arbeitsverzeichnis aus. | Kontrolle bei mehrfachen Verzeichniswechseln. |
| `:cd <pfad>` | Wechselt in ein Zielverzeichnis relativ oder absolut. | Projekte wechseln, Logs prüfen. |
| `:dryrun on` / `:dryrun off` | Aktiviert oder deaktiviert Schreib- und Ausführsperren. | Risikoarme Vorschau (`on`), finale Umsetzung (`off`). |
| `:auto on` / `:auto off` | Aktiviert oder deaktiviert automatische Bestätigung vorgeschlagener Schritte. | Automatisierte Serienaufgaben, Headless-ähnliche Abläufe. |
| `:yes` / `:no` | Bestätigt oder verwirft den zuletzt vorgeschlagenen Schritt. | Feingranulare Steuerung einzelner Aktionen. |
| `:quit` | Beendet die aktuelle GPTCode-Sitzung. | Ordnungsgemäßes Sitzungsende nach Abschluss. |

> 💡 **Hinweis:** Steuerbefehle können jederzeit eingegeben werden, auch nachdem GPTCode einen Vorschlag unterbreitet hat.

## Interaktive Nutzung
1. **Projektverzeichnis wählen**
   ```bash
   cd /pfad/zu/deinem/projekt
   ```
2. **GPTCode starten**
   ```bash
   gptcode
   ```
   Beim Start prüft GPTCode automatisch, ob `git` und `docker` im `PATH` liegen. Fehlt eines der Werkzeuge, wird der Start mit
   einer Fehlermeldung abgebrochen. `pytest` ist optional; sollte es fehlen, weist GPTCode mit einer Warnung auf die Installation
   (z. B. `pip install pytest`) hin, bevor Testläufe angefordert werden.
   Optional lassen sich Sitzungswerte temporär überschreiben:
   ```bash
   gptcode --model gpt-4o --dryrun on
   ```
   - `--model <name>` wechselt das verwendete Modell nur für die aktuelle Sitzung.
   - `--dryrun on|off` aktiviert/deaktiviert Trockenläufe ohne die Konfiguration zu ändern.
3. **Aufgaben formulieren**
   - Beschreibe Ziele und Akzeptanzkriterien natürlichsprachlich.
   - Lass dir Vorhaben bestätigen und nutze `:yes` / `:no`, um einzelne Schritte freizugeben.
4. **Sicherheitsoptionen anpassen**
   - `:dryrun on` für eine risikoarme Simulation.
   - `:auto off` für maximale Kontrolle oder `:auto on` für Fließarbeit.
5. **Resultate prüfen**
   - GPTCode zeigt Dateidiffs, Konsolenlogs und Testergebnisse an.
   - Mit `:quit` beendest du die Sitzung nach erfolgreicher Umsetzung.

### Beispiel einer manuellen Schleife
```text
> Analysiere die systemd-Unit, passe den Restart-Delay auf 10s an und starte den Dienst neu.
GPTCode: … schlägt Änderungen vor …
> :yes
GPTCode: … führt Änderung durch und zeigt diff …
> Starte jetzt den Dienst neu und zeige den Status.
GPTCode: … führt `systemctl restart` und `systemctl status` aus …
```

## Headless- & Auto-Betrieb
Der Headless-Modus (`--headless`) kombiniert klare Zielvorgaben mit automatischer Bestätigung. Verwende ihn für reproduzierbare Pipelines, CI/CD-Checks oder groß angelegte Refactorings.

### Minimalbeispiel
```bash
gptcode --headless --goal "Analysiere, teste und finalisiere dieses Projekt (systemd, Nginx, Docker, PyTest)."
```

### Erweiterte Optionen
- `--log-file /var/log/gptcode-headless.log` zum Mitschreiben der Aktionen.
- `--max-steps 200` zur Begrenzung automatischer Iterationen.
- Kombination mit `:dryrun on` im Goal-Text für konservative Abläufe.
- `--model <name>` und `--dryrun on|off` kombinieren Headless-Läufe mit temporären Sitzungswerten (z. B. spezielles Modell, Testlauf).

### Auto-Mode innerhalb interaktiver Sessions
Wenn du eine Session nicht komplett headless führen möchtest, kannst du `:auto on` aktivieren. GPTCode bestätigt dann Folgeaktionen automatisch, bis `:auto off` gesetzt wird oder ein Fehler auftritt.

### Safety-Checkliste
- Vor produktiven Deployments immer in Staging durchspielen.
- Goals präzise formulieren (z. B. inklusive Tests, Rollbacks, Notifiern).
- Logs im Blick behalten (`tail -f /var/log/gptcode-headless.log`).

## Praxis-Workflows
Die folgenden Szenarien zeigen komplette Ablaufketten, die du GPTCode vorgeben kannst. Alle Schritte lassen sich headless oder interaktiv umsetzen.

### Systemdienste mit `systemctl`
1. **Ziel formulieren**
   ```text
   Analysiere die Unit `my-service.service`, erhöhe die RestartDelay auf 10s und stelle sicher, dass der Dienst aktiv ist.
   ```
2. **Erwartete Aktionen**
   - `systemctl status my-service.service` zur Ausgangsanalyse.
   - `read_file /etc/systemd/system/my-service.service` und Anpassung via `write_file`/`apply_patch`.
   - `systemctl daemon-reload` sowie `systemctl restart my-service.service`.
   - `systemctl status` oder `systemctl is-active` zur Verifikation.
3. **Validierung**
   - GPTCode zeigt Statusausgaben an; prüfe `Active:` und `Restart`-Parameter.
   - Optional `journalctl -u my-service.service -n 20` anfordern.

### Container-Stacks mit `docker compose`
1. **Ziel formulieren**
   ```text
   Aktualisiere den Docker-Compose-Stack, führe `docker compose pull`, `docker compose up -d` und anschließend `docker compose ps` aus.
   ```
2. **Erwartete Aktionen**
   - Analyse der `docker-compose.yml` mittels `read_file`.
   - Ausführung von `docker compose pull` zur Aktualisierung der Images.
   - Deployment mit `docker compose up -d`.
   - Statusprüfung über `docker compose ps` und optional `docker compose logs <service>`.
3. **Validierung**
   - GPTCode liefert die Compose-Ausgaben, prüfe Status `running` und Port-Bindings.
   - Bei Fehlern gezielt Log-Abfragen formulieren.

### Testautomation mit `pytest`
1. **Ziel formulieren**
   ```text
   Installiere benötigte Abhängigkeiten, führe `pytest -q` aus und fasse fehlgeschlagene Tests inklusive Traceback zusammen.
   ```
2. **Erwartete Aktionen**
   - Optionale Einrichtung einer virtuellen Umgebung (`python3 -m venv .venv`).
   - Installation von `requirements.txt` via `pip install -r requirements.txt`.
   - Testlauf `pytest -q` oder projektspezifische Marker (`pytest -m integration`).
   - Zusammenfassung der Ergebnisse (bestanden, fehlgeschlagen, übersprungen).
3. **Validierung**
   - Prüfe die Exit-Codes und Berichte.
   - Fordere bei Bedarf einzelne Reports (`pytest --lf`, `pytest --maxfail=1`) an.

## Konfiguration & Speicherorte
- **Benutzerkonfiguration**: `~/.config/gptcode/config.json` (API-Key, Modell, Default-Modus).
- **Temporäre Overrides**: CLI-Flags `--model` / `--dryrun` überschreiben nur die laufende Sitzung und hinterlassen keine Spuren in der Konfiguration.
- **Logs**: konfigurierbar via `--log-file`, Standardausgabe innerhalb der Session.
- **Projektstatus**: GPTCode verändert ausschließlich freigegebene Dateien innerhalb des aktuellen Arbeitsverzeichnisses.

## Weiterführende Ressourcen
- Systemd Referenz: [systemd.unit(5)](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html)
- Docker Compose Doku: [docs.docker.com/compose](https://docs.docker.com/compose/)
- Pytest Handbuch: [docs.pytest.org](https://docs.pytest.org/)
- GPTCode Projektinformationen: [`README.md`](./README.md), [`CHANGELOG.md`](./CHANGELOG.md)
