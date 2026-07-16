import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from notenheft.models import Subject  # noqa: E402
from notenheft.storage import Storage  # noqa: E402


def test_save_and_load(tmp_path):
    data_file = tmp_path / "notenheft.json"
    storage = Storage(data_file=data_file)

    subject = Subject(name="Mathe")
    subject.add_grade(2.0, "schriftlich")
    storage.save([subject])

    loaded = storage.load()
    assert len(loaded) == 1
    assert loaded[0].name == "Mathe"
    assert loaded[0].average() == 2.0


def test_load_missing_file_returns_empty(tmp_path):
    storage = Storage(data_file=tmp_path / "does_not_exist.json")
    assert storage.load() == []


def test_backup_and_restore(tmp_path, monkeypatch):
    data_file = tmp_path / "notenheft.json"
    backup_dir = tmp_path / "backups"
    monkeypatch.setattr("notenheft.storage.BACKUP_DIR", backup_dir)

    storage = Storage(data_file=data_file)
    subject = Subject(name="Bio")
    subject.add_grade(3.0, "muendlich")
    storage.save([subject])

    backup_path = storage.create_backup()
    assert backup_path is not None
    assert backup_path.exists()

    # Daten "kaputt machen" und dann wiederherstellen
    storage.save([])
    assert storage.load() == []

    restored = storage.restore_backup(backup_path)
    assert len(restored) == 1
    assert restored[0].name == "Bio"


def test_export_csv(tmp_path):
    data_file = tmp_path / "notenheft.json"
    storage = Storage(data_file=data_file)
    subject = Subject(name="Chemie")
    subject.add_grade(1.5, "schriftlich", note="Test")
    csv_path = tmp_path / "export.csv"

    storage.export_csv([subject], csv_path)

    content = csv_path.read_text(encoding="utf-8")
    assert "Chemie" in content
    assert "1.5" in content
