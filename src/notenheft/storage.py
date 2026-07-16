"""Persistente Speicherung des Notenhefts als JSON, inkl. Backups."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from .models import Subject

DEFAULT_DATA_FILE = Path.home() / ".notenheft" / "notenheft.json"
BACKUP_DIR = Path.home() / ".notenheft" / "backups"


class Storage:
    """Kapselt Laden/Speichern der Fächer-Liste als JSON-Datei."""

    def __init__(self, data_file: Path | None = None):
        self.data_file = data_file or DEFAULT_DATA_FILE
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[Subject]:
        if not self.data_file.exists():
            return []
        try:
            raw = json.loads(self.data_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        return [Subject.from_dict(s) for s in raw.get("subjects", [])]

    def save(self, subjects: list[Subject]) -> None:
        payload = {
            "version": 2,
            "saved_at": datetime.now().isoformat(),
            "subjects": [s.to_dict() for s in subjects],
        }
        tmp_file = self.data_file.with_suffix(".tmp")
        tmp_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp_file.replace(self.data_file)

    def create_backup(self) -> Path | None:
        if not self.data_file.exists():
            return None
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"notenheft_backup_{timestamp}.json"
        shutil.copy2(self.data_file, backup_path)
        return backup_path

    def list_backups(self) -> list[Path]:
        if not BACKUP_DIR.exists():
            return []
        return sorted(BACKUP_DIR.glob("notenheft_backup_*.json"), reverse=True)

    def restore_backup(self, backup_path: Path) -> list[Subject]:
        raw = json.loads(backup_path.read_text(encoding="utf-8"))
        subjects = [Subject.from_dict(s) for s in raw.get("subjects", [])]
        self.save(subjects)
        return subjects

    def export_csv(self, subjects: list[Subject], target: Path) -> None:
        import csv

        with target.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Fach", "Note", "Art", "Datum", "Notiz"])
            for subject in subjects:
                for grade in subject.grades:
                    writer.writerow(
                        [subject.name, grade.value, grade.grade_type, grade.date_added, grade.note]
                    )
