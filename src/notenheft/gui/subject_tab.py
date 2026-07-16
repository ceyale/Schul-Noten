"""Tab: Fächerübersicht mit Notenverwaltung."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from .. import theme
from ..models import Subject
from .grade_dialog import GradeDialog


class SubjectTab(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=12)
        self.app = app  # Referenz auf die Haupt-App (hält subjects + storage)

        self._build_layout()
        self.refresh()

    def _build_layout(self):
        # Linke Spalte: Fächerliste
        left = ttk.Frame(self)
        left.pack(side="left", fill="y", padx=(0, 12))

        ttk.Label(left, text="Fächer", style="Header.TLabel").pack(anchor="w")

        self.subject_list = tk.Listbox(
            left,
            bg=theme.BG_PANEL,
            fg=theme.FG,
            selectbackground=theme.ACCENT,
            selectforeground=theme.BG,
            font=theme.FONT_MONO,
            width=22,
            height=20,
            borderwidth=0,
            highlightthickness=0,
        )
        self.subject_list.pack(fill="y", pady=6)
        self.subject_list.bind("<<ListboxSelect>>", lambda e: self._on_select())

        btn_row = ttk.Frame(left)
        btn_row.pack(fill="x", pady=4)
        ttk.Button(btn_row, text="+ Fach", command=self._add_subject).pack(side="left", expand=True, fill="x")
        ttk.Button(btn_row, text="Löschen", style="Danger.TButton", command=self._delete_subject).pack(
            side="left", expand=True, fill="x"
        )

        # Rechte Spalte: Noten des ausgewählten Fachs
        right = ttk.Frame(self)
        right.pack(side="left", fill="both", expand=True)

        self.subject_header = ttk.Label(right, text="Kein Fach ausgewählt", style="Header.TLabel")
        self.subject_header.pack(anchor="w")

        self.average_label = ttk.Label(right, text="", style="Dim.TLabel")
        self.average_label.pack(anchor="w", pady=(0, 8))

        columns = ("value", "type", "date", "note")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", height=15)
        for col, label, width in [
            ("value", "Note", 60),
            ("type", "Art", 110),
            ("date", "Datum", 100),
            ("note", "Notiz", 200),
        ]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width)
        self.tree.pack(fill="both", expand=True, pady=6)

        grade_btns = ttk.Frame(right)
        grade_btns.pack(fill="x")
        ttk.Button(grade_btns, text="+ Note", command=self._add_grade).pack(side="left", padx=(0, 6))
        ttk.Button(
            grade_btns, text="Note löschen", style="Danger.TButton", command=self._delete_grade
        ).pack(side="left")

    def _current_subject(self) -> Subject | None:
        sel = self.subject_list.curselection()
        if not sel:
            return None
        return self.app.subjects[sel[0]]

    def refresh(self):
        self.subject_list.delete(0, tk.END)
        for subject in self.app.subjects:
            avg = subject.average()
            avg_text = f"({avg})" if avg is not None else "(–)"
            self.subject_list.insert(tk.END, f"{subject.name} {avg_text}")
        self._refresh_grades()

    def _refresh_grades(self):
        self.tree.delete(*self.tree.get_children())
        subject = self._current_subject()
        if subject is None:
            self.subject_header.config(text="Kein Fach ausgewählt")
            self.average_label.config(text="")
            return
        self.subject_header.config(text=subject.name)
        avg = subject.average()
        self.average_label.config(
            text=f"Ø {avg}" if avg is not None else "Noch keine Noten"
        )
        for grade in subject.grades:
            self.tree.insert(
                "", tk.END, iid=grade.id,
                values=(grade.value, grade.grade_type, grade.date_added, grade.note),
            )

    def _on_select(self):
        self._refresh_grades()

    def _add_subject(self):
        name = simpledialog.askstring("Neues Fach", "Name des Fachs:", parent=self)
        if not name:
            return
        self.app.subjects.append(Subject(name=name))
        self.app.save()
        self.refresh()

    def _delete_subject(self):
        subject = self._current_subject()
        if subject is None:
            return
        if messagebox.askyesno("Löschen", f"Fach '{subject.name}' wirklich löschen?"):
            self.app.subjects.remove(subject)
            self.app.save()
            self.refresh()

    def _add_grade(self):
        subject = self._current_subject()
        if subject is None:
            messagebox.showinfo("Hinweis", "Bitte zuerst ein Fach auswählen.")
            return

        def on_submit(value, grade_type, note):
            subject.add_grade(value, grade_type, note)
            self.app.save()
            self.refresh()

        GradeDialog(self, on_submit)

    def _delete_grade(self):
        subject = self._current_subject()
        if subject is None:
            return
        sel = self.tree.selection()
        if not sel:
            return
        subject.remove_grade(sel[0])
        self.app.save()
        self.refresh()
