import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from notenheft.calculator import is_achievable, required_grade  # noqa: E402
from notenheft.models import Subject  # noqa: E402


def test_required_grade_written_only():
    subject = Subject(name="Mathe", written_weight=1, oral_weight=1)
    subject.add_grade(2.0, "schriftlich")
    # Ziel 2.0 im Schnitt aus 2 schriftlichen Noten -> zweite muss auch 2.0 sein
    result = required_grade(subject, target_average=2.0, next_grade_type="schriftlich")
    assert result == 2.0


def test_required_grade_mixed_weighting():
    subject = Subject(name="Deutsch", written_weight=2, oral_weight=1)
    subject.add_grade(2.0, "schriftlich")
    subject.add_grade(3.0, "muendlich")
    # total_weight aktuell = 2 (schriftlich) + 1 (mündlich) = 3
    # wir fragen: welche mündliche Note nötig für Ziel-Schnitt 2.5?
    result = required_grade(subject, target_average=2.5, next_grade_type="muendlich")
    assert result is not None


def test_is_achievable():
    assert is_achievable(1.0) is True
    assert is_achievable(6.0) is True
    assert is_achievable(0.5) is False
    assert is_achievable(6.5) is False


def test_required_grade_no_grades_yet():
    subject = Subject(name="Physik")
    result = required_grade(subject, target_average=2.0, next_grade_type="schriftlich")
    # Mit nur einer zukünftigen Note ist der Zielschnitt direkt diese Note
    assert result == 2.0
