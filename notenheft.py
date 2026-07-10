 #!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Notenheft - Ein kleines Desktop-Programm zur Verwaltung von Schulnoten.


Funktionen:

- Fächer anlegen, umbenennen, löschen

- Schriftliche und mündliche Noten je Fach erfassen

- Gewichtung schriftlich/mündlich je Fach einstellbar

- Automatische Berechnung von Fach- und Gesamtdurchschnitt

- Notenspiegel (Verteilung aller Noten) als Balkendiagramm

- Automatisches Speichern in einer JSON-Datei im Benutzerverzeichnis


Voraussetzungen: nur die Python-Standardbibliothek (tkinter, json).

Starten mit:  python3 notenheft.py

"""


import json

import os

import tkinter as tk

from tkinter import ttk, messagebox

from pathlib import Path


DATA_FILE = Path.home() / ".notenheft_data.json"


NOTE_MIN, NOTE_MAX = 1.0, 6.0


# Farben ("Papier & Rotstift"-Optik)

COL_BG = "#F6F3EC"

COL_PANEL = "#FFFDF8"

COL_LINE = "#DAD4C2"

COL_INK = "#232A33"

COL_INK_SOFT = "#5B6472"

COL_RED = "#B23B2E"

COL_GREEN = "#3F6B4C"

COL_AMBER = "#A9812E"



def note_farbe(wert):

    if wert <= 1.5:

        return COL_GREEN

    if wert <= 2.5:

        return "#5C7A50"

    if wert <= 3.5:

        return COL_AMBER

    if wert <= 4.5:

        return "#C17A3C"

    return COL_RED



class Datenhaltung:

    """Laden/Speichern der Fächer- und Notendaten als JSON."""


    def __init__(self, pfad: Path):

        self.pfad = pfad


    def laden(self):

        if not self.pfad.exists():

            return {"subjects": []}

        try:

            with open(self.pfad, "r", encoding="utf-8") as f:

                return json.load(f)

        except (json.JSONDecodeError, OSError):

            return {"subjects": []}


    def speichern(self, daten):

        try:

            with open(self.pfad, "w", encoding="utf-8") as f:

                json.dump(daten, f, ensure_ascii=False, indent=2)

        except OSError as e:

            messagebox.showerror("Speicherfehler", f"Konnte Daten nicht speichern:\n{e}")



def durchschnitt(werte):

    if not werte:

        return None

    return sum(werte) / len(werte)



def fach_durchschnitt(fach):

    schriftlich = [g["value"] for g in fach["grades"] if g["type"] == "schriftlich"]

    muendlich = [g["value"] for g in fach["grades"] if g["type"] == "muendlich"]

    a_s = durchschnitt(schriftlich)

    a_m = durchschnitt(muendlich)

    if a_s is None and a_m is None:

        return None

    if a_s is None:

        return a_m

    if a_m is None:

        return a_s

    ws, wm = fach.get("weight_schriftlich", 50), fach.get("weight_muendlich", 50)

    gesamt_gewicht = ws + wm

    if gesamt_gewicht == 0:

        return (a_s + a_m) / 2

    return (a_s * ws + a_m * wm) / gesamt_gewicht



class Notenheft(tk.Tk):

    def __init__(self):

        super().__init__()

        self.title("Notenheft")

        self.geometry("980x640")

        self.minsize(820, 560)

        self.configure(bg=COL_BG)


        self.db = Datenhaltung(DATA_FILE)

        self.daten = self.db.laden()

        self.aktuelles_fach_id = None


        self._stil_einrichten()

        self._layout_aufbauen()

        self._fachliste_aktualisieren()

        self._gesamtstatistik_aktualisieren()

        self._notenspiegel_zeichnen()


        # Beim Schließen sicherstellen, dass gespeichert wurde

        self.protocol("WM_DELETE_WINDOW", self._beenden)


    # ------------------------------------------------------------------ UI


    def _stil_einrichten(self):

        stil = ttk.Style(self)

        try:

            stil.theme_use("clam")

        except tk.TclError:

            pass


        stil.configure(".", background=COL_BG, foreground=COL_INK, font=("Segoe UI", 10))

        stil.configure("Titel.TLabel", font=("Georgia", 20, "bold"), background=COL_BG, foreground=COL_INK)

        stil.configure("Unterueberschrift.TLabel", font=("Segoe UI", 9), background=COL_BG, foreground=COL_INK_SOFT)

        stil.configure("Panel.TFrame", background=COL_PANEL)

        stil.configure("BG.TFrame", background=COL_BG)

        stil.configure("StatLabel.TLabel", font=("Consolas", 9), background=COL_PANEL, foreground=COL_INK_SOFT)

        stil.configure("StatWert.TLabel", font=("Georgia", 20, "bold"), background=COL_PANEL, foreground=COL_INK)

        stil.configure("FachName.TLabel", font=("Georgia", 15, "bold"), background=COL_PANEL, foreground=COL_INK)

        stil.configure("Spalte.TLabel", font=("Consolas", 9, "bold"), background=COL_PANEL, foreground=COL_INK_SOFT)

        stil.configure("TButton", padding=6)

        stil.configure("Treeview", rowheight=26, font=("Segoe UI", 10))

        stil.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))


    def _layout_aufbauen(self):

        kopf = ttk.Frame(self, style="BG.TFrame", padding=(20, 16, 20, 10))

        kopf.pack(fill="x")

        ttk.Label(kopf, text="Notenheft", style="Titel.TLabel").pack(side="left")

        ttk.Label(kopf, text="SCHRIFTLICH · MÜNDLICH · Ø", style="Unterueberschrift.TLabel").pack(

            side="right", pady=(10, 0)

        )


        # Gesamtstatistik-Leiste

        self.stat_frame = ttk.Frame(self, style="BG.TFrame", padding=(20, 0, 20, 14))

        self.stat_frame.pack(fill="x")


        haupt = ttk.Frame(self, style="BG.TFrame")

        haupt.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        haupt.columnconfigure(0, weight=0, minsize=230)

        haupt.columnconfigure(1, weight=1)

        haupt.rowconfigure(0, weight=1)


        # --- Linke Spalte: Fächerliste

        links = ttk.Frame(haupt, style="Panel.TFrame", padding=12)

        links.grid(row=0, column=0, sticky="nsew", padx=(0, 14))


        ttk.Label(links, text="Fächer", style="FachName.TLabel").pack(anchor="w", pady=(0, 8))


        self.fach_listbox = tk.Listbox(

            links, bg=COL_PANEL, fg=COL_INK, font=("Segoe UI", 11),

            selectbackground=COL_INK, selectforeground=COL_PANEL,

            highlightthickness=0, borderwidth=0, activestyle="none"

        )

        self.fach_listbox.pack(fill="both", expand=True, pady=(0, 10))

        self.fach_listbox.bind("<<ListboxSelect>>", self._fach_ausgewaehlt)


        neu_frame = ttk.Frame(links, style="Panel.TFrame")

        neu_frame.pack(fill="x")

        self.neues_fach_entry = ttk.Entry(neu_frame)

        self.neues_fach_entry.pack(side="left", fill="x", expand=True)

        self.neues_fach_entry.bind("<Return>", lambda e: self._fach_hinzufuegen())

        ttk.Button(neu_frame, text="+", width=3, command=self._fach_hinzufuegen).pack(side="left", padx=(6, 0))


        ttk.Button(links, text="Fach löschen", command=self._fach_loeschen).pack(fill="x", pady=(10, 0))


        # --- Rechte Spalte: Notebook mit Details & Notenspiegel

        self.notebook = ttk.Notebook(haupt)

        self.notebook.grid(row=0, column=1, sticky="nsew")


        self.detail_frame = ttk.Frame(self.notebook, style="Panel.TFrame", padding=16)

        self.spiegel_frame = ttk.Frame(self.notebook, style="Panel.TFrame", padding=16)

        self.notebook.add(self.detail_frame, text="  Noten  ")

        self.notebook.add(self.spiegel_frame, text="  Notenspiegel  ")


        self._detailbereich_aufbauen()

        self._notenspiegel_aufbauen()


    # -------------------------------------------------------- Detailbereich


    def _detailbereich_aufbauen(self):

        self.detail_platzhalter = ttk.Label(

            self.detail_frame,

            text="Wähle links ein Fach aus oder lege ein neues an.",

            style="Unterueberschrift.TLabel",

        )

        self.detail_platzhalter.pack(expand=True)


        self.detail_inhalt = ttk.Frame(self.detail_frame, style="Panel.TFrame")


        kopf = ttk.Frame(self.detail_inhalt, style="Panel.TFrame")

        kopf.pack(fill="x", pady=(0, 12))

        self.fach_titel_label = ttk.Label(kopf, text="", style="FachName.TLabel")

        self.fach_titel_label.pack(side="left")

        self.fach_avg_label = ttk.Label(kopf, text="", font=("Consolas", 20, "bold"), background=COL_PANEL)

        self.fach_avg_label.pack(side="right")


        gewicht_frame = ttk.Frame(self.detail_inhalt, style="Panel.TFrame")

        gewicht_frame.pack(fill="x", pady=(0, 14))

        ttk.Label(gewicht_frame, text="Gewichtung:", style="StatLabel.TLabel").pack(side="left")

        ttk.Label(gewicht_frame, text="  Schriftlich", style="StatLabel.TLabel").pack(side="left", padx=(10, 2))

        self.gewicht_s_var = tk.StringVar()

        gs = ttk.Spinbox(gewicht_frame, from_=0, to=100, width=4, textvariable=self.gewicht_s_var,

                          command=self._gewicht_geaendert)

        gs.pack(side="left")

        gs.bind("<Return>", lambda e: self._gewicht_geaendert())

        gs.bind("<FocusOut>", lambda e: self._gewicht_geaendert())

        ttk.Label(gewicht_frame, text="%   Mündlich", style="StatLabel.TLabel").pack(side="left", padx=(10, 2))

        self.gewicht_m_var = tk.StringVar()

        gm = ttk.Spinbox(gewicht_frame, from_=0, to=100, width=4, textvariable=self.gewicht_m_var,

                          command=self._gewicht_geaendert)

        gm.pack(side="left")

        gm.bind("<Return>", lambda e: self._gewicht_geaendert())

        gm.bind("<FocusOut>", lambda e: self._gewicht_geaendert())

        ttk.Label(gewicht_frame, text="%", style="StatLabel.TLabel").pack(side="left")


        # Jede Änderung an der Gewichtung sofort speichern (auch beim reinen Tippen,

        # nicht erst bei Enter/Fokuswechsel)

        self.gewicht_s_var.trace_add("write", lambda *a: self._gewicht_geaendert())

        self.gewicht_m_var.trace_add("write", lambda *a: self._gewicht_geaendert())


        spalten = ttk.Frame(self.detail_inhalt, style="Panel.TFrame")

        spalten.pack(fill="both", expand=True)

        spalten.columnconfigure(0, weight=1)

        spalten.columnconfigure(1, weight=1)


        self.schriftlich_tree, self.schriftlich_entry = self._notenspalte_aufbauen(

            spalten, "Schriftlich", "schriftlich", 0

        )

        self.muendlich_tree, self.muendlich_entry = self._notenspalte_aufbauen(

            spalten, "Mündlich", "muendlich", 1

        )


    def _notenspalte_aufbauen(self, eltern, titel, typ, spalte):

        rahmen = ttk.Frame(eltern, style="Panel.TFrame", padding=(0, 0, 12 if spalte == 0 else 0, 0))

        rahmen.grid(row=0, column=spalte, sticky="nsew", padx=(0, 10) if spalte == 0 else (10, 0))


        ttk.Label(rahmen, text=titel, style="Spalte.TLabel").pack(anchor="w", pady=(0, 4))


        baum = ttk.Treeview(rahmen, columns=("note",), show="headings", height=8, selectmode="browse")

        baum.heading("note", text="Note")

        baum.column("note", width=80, anchor="center")

        baum.pack(fill="both", expand=True)


        loesch_btn = ttk.Button(rahmen, text="Ausgewählte Note löschen",

                                 command=lambda: self._note_loeschen(typ, baum))

        loesch_btn.pack(fill="x", pady=(6, 6))


        eingabe_frame = ttk.Frame(rahmen, style="Panel.TFrame")

        eingabe_frame.pack(fill="x")

        eintrag = ttk.Entry(eingabe_frame, width=8)

        eintrag.pack(side="left")

        eintrag.bind("<Return>", lambda e: self._note_hinzufuegen(typ, eintrag))

        ttk.Button(eingabe_frame, text="Note hinzufügen (1–6)",

                   command=lambda: self._note_hinzufuegen(typ, eintrag)).pack(side="left", padx=(6, 0))


        return baum, eintrag


    # -------------------------------------------------------- Notenspiegel


    def _notenspiegel_aufbauen(self):

        ttk.Label(self.spiegel_frame, text="Notenspiegel", style="FachName.TLabel").pack(anchor="w")

        ttk.Label(

            self.spiegel_frame,

            text="Verteilung aller erfassten Noten über alle Fächer",

            style="Unterueberschrift.TLabel",

        ).pack(anchor="w", pady=(0, 12))


        self.spiegel_canvas = tk.Canvas(self.spiegel_frame, bg=COL_PANEL, highlightthickness=0, height=280)

        self.spiegel_canvas.pack(fill="both", expand=True)

        self.spiegel_canvas.bind("<Configure>", lambda e: self._notenspiegel_zeichnen())


        legende = ttk.Frame(self.spiegel_frame, style="Panel.TFrame")

        legende.pack(anchor="w", pady=(10, 0))

        self._legenden_eintrag(legende, COL_INK, "Schriftlich")

        self._legenden_eintrag(legende, COL_RED, "Mündlich")


    def _legenden_eintrag(self, eltern, farbe, text):

        f = ttk.Frame(eltern, style="Panel.TFrame")

        f.pack(side="left", padx=(0, 16))

        c = tk.Canvas(f, width=12, height=12, bg=COL_PANEL, highlightthickness=0)

        c.create_rectangle(0, 0, 12, 12, fill=farbe, outline="")

        c.pack(side="left", padx=(0, 5))

        ttk.Label(f, text=text, style="StatLabel.TLabel").pack(side="left")


    def _notenspiegel_zeichnen(self):

        canvas = self.spiegel_canvas

        canvas.delete("all")

        breite = max(canvas.winfo_width(), 400)

        hoehe = max(canvas.winfo_height(), 220)


        eimer = {i: {"s": 0, "m": 0} for i in range(1, 7)}

        for fach in self.daten["subjects"]:

            for note in fach["grades"]:

                idx = min(6, max(1, round(note["value"])))

                if note["type"] == "schriftlich":

                    eimer[idx]["s"] += 1

                else:

                    eimer[idx]["m"] += 1


        max_anzahl = max(1, max(b["s"] + b["m"] for b in eimer.values()))

        rand_unten = 30

        max_balken_hoehe = hoehe - rand_unten - 20

        gruppenbreite = breite / 6

        balkenbreite = min(30, gruppenbreite / 3)


        canvas.create_line(0, hoehe - rand_unten, breite, hoehe - rand_unten, fill=COL_LINE)


        for i in range(1, 7):

            b = eimer[i]

            mitte = (i - 1) * gruppenbreite + gruppenbreite / 2

            h_s = (b["s"] / max_anzahl) * max_balken_hoehe

            h_m = (b["m"] / max_anzahl) * max_balken_hoehe


            x_s = mitte - balkenbreite - 3

            x_m = mitte + 3


            if h_s > 0:

                canvas.create_rectangle(

                    x_s, hoehe - rand_unten - h_s, x_s + balkenbreite, hoehe - rand_unten,

                    fill=COL_INK, outline=""

                )

            if h_m > 0:

                canvas.create_rectangle(

                    x_m, hoehe - rand_unten - h_m, x_m + balkenbreite, hoehe - rand_unten,

                    fill=COL_RED, outline=""

                )


            gesamt = b["s"] + b["m"]

            if gesamt > 0:

                y_text = hoehe - rand_unten - max(h_s, h_m) - 10

                canvas.create_text(mitte, y_text, text=str(gesamt), fill=COL_INK_SOFT, font=("Consolas", 9))


            canvas.create_text(mitte, hoehe - rand_unten + 14, text=str(i), fill=COL_INK_SOFT, font=("Consolas", 10))


    # -------------------------------------------------------- Aktionen: Fach


    def _fachliste_aktualisieren(self):

        self.fach_listbox.delete(0, tk.END)

        for fach in self.daten["subjects"]:

            avg = fach_durchschnitt(fach)

            text = fach["name"] + (f"   ({avg:.2f})" if avg is not None else "")

            self.fach_listbox.insert(tk.END, text)


        if self.aktuelles_fach_id is not None:

            for i, fach in enumerate(self.daten["subjects"]):

                if fach["id"] == self.aktuelles_fach_id:

                    self.fach_listbox.selection_set(i)

                    break


    def _fach_hinzufuegen(self):

        name = self.neues_fach_entry.get().strip()

        if not name:

            return

        neues_fach = {

            "id": os.urandom(6).hex(),

            "name": name,

            "weight_schriftlich": 50,

            "weight_muendlich": 50,

            "grades": [],

        }

        self.daten["subjects"].append(neues_fach)

        self.neues_fach_entry.delete(0, tk.END)

        self.aktuelles_fach_id = neues_fach["id"]

        self._speichern_und_aktualisieren()


    def _fach_loeschen(self):

        fach = self._aktuelles_fach()

        if fach is None:

            messagebox.showinfo("Kein Fach ausgewählt", "Bitte zuerst ein Fach in der Liste auswählen.")

            return

        if not messagebox.askyesno("Fach löschen", f'"{fach["name"]}" wirklich löschen?'):

            return

        self.daten["subjects"] = [f for f in self.daten["subjects"] if f["id"] != fach["id"]]

        self.aktuelles_fach_id = None

        self._speichern_und_aktualisieren()


    def _fach_ausgewaehlt(self, event=None):

        auswahl = self.fach_listbox.curselection()

        if not auswahl:

            return

        fach = self.daten["subjects"][auswahl[0]]

        self.aktuelles_fach_id = fach["id"]

        self._detailbereich_zeigen(fach)


    def _aktuelles_fach(self):

        for fach in self.daten["subjects"]:

            if fach["id"] == self.aktuelles_fach_id:

                return fach

        return None


    def _detailbereich_zeigen(self, fach):

        self.detail_platzhalter.pack_forget()

        self.detail_inhalt.pack(fill="both", expand=True)


        self.fach_titel_label.config(text=fach["name"])

        avg = fach_durchschnitt(fach)

        if avg is not None:

            self.fach_avg_label.config(text=f"{avg:.2f}", foreground=note_farbe(avg))

        else:

            self.fach_avg_label.config(text="–", foreground=COL_INK_SOFT)


        self.gewicht_s_var.set(str(fach.get("weight_schriftlich", 50)))

        self.gewicht_m_var.set(str(fach.get("weight_muendlich", 50)))


        self._notenliste_aktualisieren(self.schriftlich_tree, fach, "schriftlich")

        self._notenliste_aktualisieren(self.muendlich_tree, fach, "muendlich")


    def _notenliste_aktualisieren(self, baum, fach, typ):

        baum.delete(*baum.get_children())

        for note in fach["grades"]:

            if note["type"] == typ:

                baum.insert("", tk.END, iid=note["id"], values=(f'{note["value"]:.1f}',))


    def _gewicht_geaendert(self):

        fach = self._aktuelles_fach()

        if fach is None:

            return

        try:

            ws = max(0, min(100, int(self.gewicht_s_var.get())))

            wm = max(0, min(100, int(self.gewicht_m_var.get())))

        except ValueError:

            return

        fach["weight_schriftlich"] = ws

        fach["weight_muendlich"] = wm

        self._speichern_und_aktualisieren()


    # -------------------------------------------------------- Aktionen: Noten


    def _note_hinzufuegen(self, typ, eintrag_widget):

        fach = self._aktuelles_fach()

        if fach is None:

            return

        text = eintrag_widget.get().strip().replace(",", ".")

        try:

            wert = float(text)

        except ValueError:

            messagebox.showwarning("Ungültige Note", "Bitte eine Zahl zwischen 1 und 6 eingeben.")

            return

        if not (NOTE_MIN <= wert <= NOTE_MAX):

            messagebox.showwarning("Ungültige Note", "Die Note muss zwischen 1 und 6 liegen.")

            return

        fach["grades"].append({"id": os.urandom(6).hex(), "type": typ, "value": round(wert, 1)})

        eintrag_widget.delete(0, tk.END)

        self._speichern_und_aktualisieren()


    def _note_loeschen(self, typ, baum):

        fach = self._aktuelles_fach()

        if fach is None:

            return

        auswahl = baum.selection()

        if not auswahl:

            return

        note_id = auswahl[0]

        fach["grades"] = [g for g in fach["grades"] if g["id"] != note_id]

        self._speichern_und_aktualisieren()


    # -------------------------------------------------------- Gesamtstatistik


    def _gesamtstatistik_aktualisieren(self):

        for widget in self.stat_frame.winfo_children():

            widget.destroy()


        faecher = self.daten["subjects"]

        fach_durchschnitte = [d for d in (fach_durchschnitt(f) for f in faecher) if d is not None]

        alle_noten = [g["value"] for f in faecher for g in f["grades"]]


        gesamt_avg = durchschnitt(fach_durchschnitte)

        beste = min(alle_noten) if alle_noten else None

        schwaechste = max(alle_noten) if alle_noten else None


        self._stat_karte(self.stat_frame, "Gesamtschnitt", f"{gesamt_avg:.2f}" if gesamt_avg is not None else "–",

                          note_farbe(gesamt_avg) if gesamt_avg is not None else COL_INK)

        self._stat_karte(self.stat_frame, "Fächer", str(len(faecher)))

        self._stat_karte(self.stat_frame, "Noten erfasst", str(len(alle_noten)))

        self._stat_karte(

            self.stat_frame, "Beste / Schwächste",

            f'{beste:.1f} / {schwaechste:.1f}' if alle_noten else "– / –"

        )


    def _stat_karte(self, eltern, label, wert, farbe=COL_INK):

        karte = ttk.Frame(eltern, style="Panel.TFrame", padding=(16, 10))

        karte.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ttk.Label(karte, text=label.upper(), style="StatLabel.TLabel").pack(anchor="w")

        wert_label = tk.Label(karte, text=wert, font=("Georgia", 20, "bold"), bg=COL_PANEL, fg=farbe)

        wert_label.pack(anchor="w")


    # -------------------------------------------------------- Speichern/Beenden


    def _speichern_und_aktualisieren(self):

        self.db.speichern(self.daten)

        self._fachliste_aktualisieren()

        fach = self._aktuelles_fach()

        if fach is not None:

            self._detailbereich_zeigen(fach)

        self._gesamtstatistik_aktualisieren()

        self._notenspiegel_zeichnen()


    def _beenden(self):

        self.db.speichern(self.daten)

        self.destroy()



if __name__ == "__main__":

    app = Notenheft()

    app.mainloop() 