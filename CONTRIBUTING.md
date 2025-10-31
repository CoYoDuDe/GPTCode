# Beitrag leisten

Vielen Dank für dein Interesse an einer Mitarbeit an diesem Projekt. Um eine reibungslose Zusammenarbeit sicherzustellen, folge bitte den folgenden Leitlinien.

## Entwicklungsumgebung einrichten
1. Repository forken und lokal klonen.
2. Python 3.10 oder neuer installieren.
3. Virtuelle Umgebung anlegen und aktivieren:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   ```
4. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```
5. Optional: Vorhandene Beispielskripte in `docs/` lesen, um den Projektaufbau zu verstehen.

## Branch- und PR-Workflow
- Entwickle neue Features und Bugfixes stets auf einem eigenen Branch nach dem Schema `feature/<kurzbeschreibung>` oder `fix/<kurzbeschreibung>`.
- Halte deinen Branch regelmäßig mit `main` synchron (`git fetch` + `git rebase`).
- Erstelle Pull Requests frühzeitig, damit das Review-Team Feedback geben kann.
- Beschreibe im PR klar das Problem, die Lösung und relevante Auswirkungen auf bestehende Funktionen.

## Tests
- Führe vor jedem Commit die verfügbaren Tests aus:
  ```bash
  pytest
  ```
- Stelle sicher, dass neue oder geänderte Funktionen durch passende Tests abgedeckt sind.
- Dokumentiere im PR, welche Tests durchgeführt wurden.

Vielen Dank für deinen Beitrag! Gemeinsam halten wir das Projekt stabil, wartbar und zukunftssicher.
