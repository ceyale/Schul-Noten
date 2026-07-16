"""Tab: Statistik-Übersicht über alle Fächer."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .. import theme


class StatisticsTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app

        ttk.Label(self, text="Statistik", style="Header.TLabel").pack(anchor="w")

        self.overall_label = ttk.Label(self, text="", style="Dim.TLabel")
        self.overall_label.pack(anchor="w", pady=(0, 12))

        columns = ("subject", "average", "count", "trend")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=18)
        for col, label, width in [
            ("subject", "Fach", 180),
            ("average", "Schnitt", 100),
            ("count", "Anzahl Noten", 120),
            ("trend", "Tendenz", 100),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width)
        self.tree.pack(fill="both", expand=True)

        ttk.Button(self, text="Aktualisieren", command=self.refresh).pack(anchor="w", pady=8)

    def _trend(self, subject) -> str:
        """Vergleicht die letzten zwei Noten, um grob eine Tendenz anzuzeigen."""
        grades = sorted(subject.grades, key=lambda g: g.date_added)
        if len(grades) < 2:
            return "–"
        last, prev = grades[-1].value, grades[-2].value
        if last < prev:
            return "▲ besser"
        if last > prev:
            return "▼ schlechter"
        return "= gleich"

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        all_averages = []
        for subject in self.app.subjects:
            avg = subject.average()
            if avg is not None:
                all_averages.append(avg)
            self.tree.insert(
                "",
                tk.END,
                values=(
                    subject.name,
                    avg if avg is not None else "–",
                    len(subject.grades),
                    self._trend(subject),
                ),
            )
        if all_averages:
            overall = round(sum(all_averages) / len(all_averages), 2)
            self.overall_label.config(text=f"Gesamtschnitt über alle Fächer: {overall}")
        else:
            self.overall_label.config(text="Noch keine Noten vorhanden.")
