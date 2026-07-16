# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden hier dokumentiert.

## [2.0.0] - 2026-07-15

### Hinzugefügt
- Komplette Umstrukturierung in ein sauberes Paket (`src/notenheft/...`)
- Statistik-Tab mit Gesamtschnitt und Tendenz pro Fach
- Notenrechner-Tab: berechnet die benötigte nächste Note für einen Zielschnitt
- Backup-System (manuell auslösbar über das Menü)
- CSV-Export aller Noten
- Dark-Terminal-Theme für die komplette Oberfläche
- Unit-Tests für Modelle, Storage und Notenrechner (pytest)
- GitHub Actions Workflow für automatische Tests bei jedem Push

### Geändert
- Persistenz nutzt jetzt atomare Schreibvorgänge (`.tmp` → Umbenennen), um Datenverlust bei Absturz zu vermeiden

## [1.0.0]

- Erste Version: Tkinter-Notenheft mit Fachverwaltung, schriftlich/mündlich getrennt, konfigurierbarer Gewichtung, JSON-Speicherung
