"""Dialog zum Hinzufügen einer neuen Note."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .. import theme


class GradeDialog(tk.Toplevel):
    def __init__(self, parent, on_submit):
        super().__init__(parent)
        self.title("Neue Note")
        self.configure(bg=theme.BG)
        self.resizable(False, False)
        self.on_submit = on_submit
        self.transient(parent)
        self.grab_set()

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Note (1-6):").grid(row=0, column=0, sticky="w", pady=4)
        self.value_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.value_var, width=10).grid(row=0, column=1, pady=4)

        ttk.Label(frame, text="Art:").grid(row=1, column=0, sticky="w", pady=4)
        self.type_var = tk.StringVar(value="schriftlich")
        ttk.Combobox(
            frame,
            textvariable=self.type_var,
            values=["schriftlich", "muendlich"],
            state="readonly",
            width=15,
        ).grid(row=1, column=1, pady=4)

        ttk.Label(frame, text="Notiz (optional):").grid(row=2, column=0, sticky="w", pady=4)
        self.note_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.note_var, width=20).grid(row=2, column=1, pady=4)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn_frame, text="Speichern", command=self._submit).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Abbrechen", command=self.destroy).pack(side="left", padx=4)

        self.bind("<Return>", lambda e: self._submit())

    def _submit(self):
        try:
            value = float(self.value_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Fehler", "Bitte eine gültige Zahl eingeben.")
            return
        if not (1.0 <= value <= 6.0):
            messagebox.showerror("Fehler", "Note muss zwischen 1 und 6 liegen.")
            return
        self.on_submit(value, self.type_var.get(), self.note_var.get())
        self.destroy()
