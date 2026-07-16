"""Hauptfenster der Notenheft-App."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .. import theme
from ..storage import Storage
from .calculator_tab import CalculatorTab
from .statistics_tab import StatisticsTab
from .subject_tab import SubjectTab


class NotenheftApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Notenheft")
        self.geometry("820x560")
        theme.apply_theme(self)

        self.storage = Storage()
        self.subjects = self.storage.load()

        self._build_menu()
        self._build_tabs()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Backup erstellen", command=self._create_backup)
        file_menu.add_command(label="Backup wiederherstellen", command=self._restore_backup)
        file_menu.add_command(label="Als CSV exportieren", command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self._on_close)
        menubar.add_cascade(label="Datei", menu=file_menu)

        self.config(menu=menubar)

    def _build_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.subject_tab = SubjectTab(notebook, self)
        self.statistics_tab = StatisticsTab(notebook, self)
        self.calculator_tab = CalculatorTab(notebook, self)

        notebook.add(self.subject_tab, text="Fächer")
        notebook.add(self.statistics_tab, text="Statistik")
        notebook.add(self.calculator_tab, text="Notenrechner")

        notebook.bind("<<NotebookTabChanged>>", lambda e: self._on_tab_changed())

    def _on_tab_changed(self):
        # Statistik & Rechner aktualisieren, sobald der Tab geöffnet wird
        self.statistics_tab.refresh()
        self.calculator_tab.refresh()

    def save(self):
        """Autosave: wird nach jeder Änderung aufgerufen."""
        self.storage.save(self.subjects)

    def _create_backup(self):
        path = self.storage.create_backup()
        if path:
            messagebox.showinfo("Backup", f"Backup erstellt:\n{path}")
        else:
            messagebox.showinfo("Backup", "Noch keine Daten zum Sichern vorhanden.")

    def _restore_backup(self):
        backups = self.storage.list_backups()
        if not backups:
            messagebox.showinfo("Wiederherstellen", "Keine Backups gefunden.")
            return
        # Einfache Auswahl über einen Dateidialog im Backup-Ordner
        path = filedialog.askopenfilename(
            initialdir=str(backups[0].parent),
            title="Backup auswählen",
            filetypes=[("JSON-Dateien", "*.json")],
        )
        if not path:
            return
        if messagebox.askyesno("Wiederherstellen", "Aktuelle Daten werden überschrieben. Fortfahren?"):
            from pathlib import Path

            self.subjects = self.storage.restore_backup(Path(path))
            self.subject_tab.refresh()
            self.statistics_tab.refresh()
            self.calculator_tab.refresh()

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV-Dateien", "*.csv")],
            initialfile="notenheft_export.csv",
        )
        if not path:
            return
        from pathlib import Path

        self.storage.export_csv(self.subjects, Path(path))
        messagebox.showinfo("Export", f"Export gespeichert:\n{path}")

    def _on_close(self):
        self.save()
        self.destroy()


def run():
    app = NotenheftApp()
    app.mainloop()
