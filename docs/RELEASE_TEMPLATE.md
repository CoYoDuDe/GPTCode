# Release- und Git-Tag-Checkliste

Diese Vorlage unterstützt dabei, Releases konsistent vorzubereiten und zu veröffentlichen.

1. **Version festlegen**
   - `VERSION` auf die neue SemVer-Version aktualisieren.
   - Abschnitt `## [Unreleased]` im `CHANGELOG.md` prüfen und neue Version mit Datum eintragen.
2. **Änderungen finalisieren**
   - Sicherstellen, dass alle relevanten Commits in `main`/`master` gemergt sind.
   - Tests und Qualitätsprüfungen durchführen.
3. **Release-Branch / Tag vorbereiten**
   - Optional: Release-Branch erstellen, z. B. `release/vX.Y.Z`.
   - Git-Tag setzen: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.
4. **Dokumentation aktualisieren**
   - README auf Hinweise zur neuen Version überprüfen.
   - `docs/` oder weitere Handbücher auf Konsistenz prüfen.
5. **Release veröffentlichen**
   - Tag pushen: `git push origin vX.Y.Z` (ggf. inkl. Branch).
   - GitHub Release erstellen: Changelog-Eintrag einfügen, Binärdateien anhängen (falls nötig).
6. **Nachbereitung**
   - `CHANGELOG.md` neuen Abschnitt `## [Unreleased]` vorbereiten (falls geleert).
   - Interne Stakeholder informieren und Deployment planen.

> Hinweis: Dieser Prozess orientiert sich an bewährten Git-Release-Workflows und bleibt kompatibel mit SetupHelper-Add-ons und Automatisierungen.
