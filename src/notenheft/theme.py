"""Dark Terminal-Style Theme für die Tkinter-Oberfläche."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

BG = "#0d1117"
BG_PANEL = "#161b22"
FG = "#00ff9c"
FG_DIM = "#8b949e"
ACCENT = "#39d353"
DANGER = "#ff5555"
FONT_MONO = ("Consolas", 11)
FONT_MONO_BOLD = ("Consolas", 11, "bold")
FONT_HEADER = ("Consolas", 14, "bold")


def apply_theme(root: tk.Tk) -> None:
    root.configure(bg=BG)
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=BG)
    style.configure("Panel.TFrame", background=BG_PANEL)

    style.configure(
        "TLabel", background=BG, foreground=FG, font=FONT_MONO
    )
    style.configure(
        "Header.TLabel", background=BG, foreground=ACCENT, font=FONT_HEADER
    )
    style.configure(
        "Dim.TLabel", background=BG, foreground=FG_DIM, font=FONT_MONO
    )

    style.configure(
        "TButton",
        background=BG_PANEL,
        foreground=FG,
        font=FONT_MONO_BOLD,
        borderwidth=1,
        focusthickness=0,
        padding=6,
    )
    style.map(
        "TButton",
        background=[("active", ACCENT)],
        foreground=[("active", BG)],
    )

    style.configure(
        "Danger.TButton", background=BG_PANEL, foreground=DANGER, font=FONT_MONO_BOLD
    )
    style.map("Danger.TButton", background=[("active", DANGER)], foreground=[("active", BG)])

    style.configure(
        "TNotebook", background=BG, borderwidth=0
    )
    style.configure(
        "TNotebook.Tab",
        background=BG_PANEL,
        foreground=FG_DIM,
        padding=(12, 6),
        font=FONT_MONO_BOLD,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", BG)],
        foreground=[("selected", ACCENT)],
    )

    style.configure(
        "Treeview",
        background=BG_PANEL,
        fieldbackground=BG_PANEL,
        foreground=FG,
        font=FONT_MONO,
        rowheight=26,
        borderwidth=0,
    )
    style.configure(
        "Treeview.Heading",
        background=BG,
        foreground=ACCENT,
        font=FONT_MONO_BOLD,
        borderwidth=0,
    )
    style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", BG)])

    style.configure(
        "TEntry",
        fieldbackground=BG_PANEL,
        foreground=FG,
        insertcolor=FG,
        font=FONT_MONO,
        borderwidth=1,
    )
    style.configure(
        "TCombobox",
        fieldbackground=BG_PANEL,
        background=BG_PANEL,
        foreground=FG,
        font=FONT_MONO,
    )
