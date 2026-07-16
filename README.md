#  Notenheft

Eine Desktop-Notenverwaltung für das deutsche 1–6 Notensystem, gebaut mit Python & Tkinter im dunklen Terminal-Stil.

![Tests](https://github.com/DEIN-USERNAME/notenheft/actions/workflows/tests.yml/badge.svg)

## Features

- **Fächerverwaltung** – beliebig viele Fächer anlegen, löschen
- **Schriftlich / mündlich getrennt** – mit konfigurierbarer Gewichtung pro Fach
- **Automatische Berechnung** des gewichteten Notenschnitts
- **Statistik-Tab** – Gesamtschnitt über alle Fächer + Tendenz (besser/schlechter)
- **Notenrechner** – "Welche Note brauche ich mindestens, um meinen Zielschnitt zu erreichen?"
- **Autosave** – jede Änderung wird sofort gespeichert
- **Backup & Wiederherstellung** – manuell auslösbar über das Menü
- **CSV-Export** aller Noten
- **Dark-Terminal-UI**

##  Screenshots

_(Screenshots hier einfügen, siehe `docs/screenshots/`)_

##  Installation & Start

Voraussetzung: Python 3.10 oder neuer (Tkinter ist bei den meisten Python-Installationen bereits enthalten).

```bash
git clone https://github.com/DEIN-USERNAME/notenheft.git
cd notenheft
pip install -r requirements.txt
python src/main.py
```

##  Tests ausführen

```bash
pip install -r requirements.txt
pytest tests/ -v
```

##  Datenspeicherung

Die Notendaten werden lokal unter `~/.notenheft/notenheft.json` gespeichert – nicht im Repository, damit private Noten nicht versehentlich hochgeladen werden (siehe `.gitignore`).

## Technologien

- Python 3
- Tkinter / ttk (GUI)
- pytest (Tests)
- GitHub Actions (CI)

##  Lizenz

MIT – siehe [LICENSE](LICENSE)
