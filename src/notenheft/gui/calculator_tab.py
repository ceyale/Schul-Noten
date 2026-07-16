"""Tab: Notenrechner - 'Was brauche ich für meine Zielnote?'"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from ..calculator import is_achievable, required_grade


class CalculatorTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app

        ttk.Label(self, text="Notenrechner", style="Header.TLabel").pack(anchor="w", pady=(0, 12))

        form = ttk.Frame(self)
        form.pack(anchor="w")

        ttk.Label(form, text="Fach:").grid(row=0, column=0, sticky="w", pady=4)
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(form, textvariable=self.subject_var, state="readonly", width=25)
        self.subject_combo.grid(row=0, column=1, pady=4)

        ttk.Label(form, text="Zielschnitt:").grid(row=1, column=0, sticky="w", pady=4)
        self.target_var = tk.StringVar(value="2.0")
        ttk.Entry(form, textvariable=self.target_var, width=10).grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Nächste Note ist:").grid(row=2, column=0, sticky="w", pady=4)
        self.type_var = tk.StringVar(value="schriftlich")
        ttk.Combobox(
            form, textvariable=self.type_var, values=["schriftlich", "muendlich"],
            state="readonly", width=15,
        ).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Button(form, text="Berechnen", command=self._calculate).grid(
            row=3, column=0, columnspan=2, pady=12
        )

        self.result_label = ttk.Label(self, text="", style="Header.TLabel")
        self.result_label.pack(anchor="w", pady=(12, 0))

        self.refresh()

    def refresh(self):
        names = [s.name for s in self.app.subjects]
        self.subject_combo["values"] = names
        if names and not self.subject_var.get():
            self.subject_var.set(names[0])

    def _calculate(self):
        name = self.subject_var.get()
        subject = next((s for s in self.app.subjects if s.name == name), None)
        if subject is None:
            messagebox.showinfo("Hinweis", "Bitte ein Fach auswählen.")
            return
        try:
            target = float(self.target_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Fehler", "Ungültiger Zielschnitt.")
            return

        result = required_grade(subject, target, self.type_var.get())
        if result is None:
            self.result_label.config(text="Berechnung nicht möglich (Gewichtung prüfen).")
        elif is_achievable(result):
            self.result_label.config(text=f"Du brauchst mindestens Note {result}")
        elif result < 1.0:
            self.result_label.config(text="Ziel bereits erreicht/übertroffen. 🎉")
        else:
            self.result_label.config(text=f"Nicht erreichbar (rechnerisch {result} nötig).")
