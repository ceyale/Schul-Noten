import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from notenheft.models import Subject  # noqa: E402


def test_average_none_without_grades():
    subject = Subject(name="Mathe")
    assert subject.average() is None


def test_average_written_only():
    subject = Subject(name="Mathe", written_weight=2, oral_weight=1)
    subject.add_grade(2.0, "schriftlich")
    subject.add_grade(4.0, "schriftlich")
    assert subject.average() == 3.0


def test_average_weighted_written_and_oral():
    subject = Subject(name="Deutsch", written_weight=2, oral_weight=1)
    subject.add_grade(2.0, "schriftlich")  # Schnitt schriftlich: 2.0, Gewicht 2
    subject.add_grade(4.0, "muendlich")  # Schnitt mündlich: 4.0, Gewicht 1
    # (2.0*2 + 4.0*1) / 3 = 8/3 = 2.6667 -> gerundet 2.67
    assert subject.average() == 2.67


def test_remove_grade():
    subject = Subject(name="Physik")
    grade = subject.add_grade(3.0, "schriftlich")
    assert subject.remove_grade(grade.id) is True
    assert subject.average() is None


def test_serialization_roundtrip():
    subject = Subject(name="Englisch")
    subject.add_grade(1.0, "schriftlich", note="Klassenarbeit 1")
    data = subject.to_dict()
    restored = Subject.from_dict(data)
    assert restored.name == subject.name
    assert restored.average() == subject.average()
    assert restored.grades[0].note == "Klassenarbeit 1"
