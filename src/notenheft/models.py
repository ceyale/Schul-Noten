"""Datenmodelle für das Notenheft: Note, Fach."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

GradeType = Literal["schriftlich", "muendlich"]


@dataclass
class Grade:
    """Eine einzelne Note."""

    value: float
    grade_type: GradeType
    date_added: str = field(default_factory=lambda: date.today().isoformat())
    note: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "value": self.value,
            "grade_type": self.grade_type,
            "date_added": self.date_added,
            "note": self.note,
        }

    @staticmethod
    def from_dict(data: dict) -> "Grade":
        return Grade(
            value=data["value"],
            grade_type=data["grade_type"],
            date_added=data.get("date_added", date.today().isoformat()),
            note=data.get("note", ""),
            id=data.get("id", uuid.uuid4().hex[:8]),
        )


@dataclass
class Subject:
    """Ein Schulfach mit Noten und Gewichtung."""

    name: str
    written_weight: float = 2.0  # z.B. schriftlich zählt doppelt
    oral_weight: float = 1.0
    grades: list[Grade] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def add_grade(self, value: float, grade_type: GradeType, note: str = "") -> Grade:
        grade = Grade(value=value, grade_type=grade_type, note=note)
        self.grades.append(grade)
        return grade

    def remove_grade(self, grade_id: str) -> bool:
        before = len(self.grades)
        self.grades = [g for g in self.grades if g.id != grade_id]
        return len(self.grades) < before

    def average(self) -> float | None:
        """Gewichteter Durchschnitt. None, wenn keine Noten vorhanden."""
        written = [g.value for g in self.grades if g.grade_type == "schriftlich"]
        oral = [g.value for g in self.grades if g.grade_type == "muendlich"]

        total_weight = 0.0
        weighted_sum = 0.0

        if written:
            w_avg = sum(written) / len(written)
            weighted_sum += w_avg * self.written_weight
            total_weight += self.written_weight
        if oral:
            o_avg = sum(oral) / len(oral)
            weighted_sum += o_avg * self.oral_weight
            total_weight += self.oral_weight

        if total_weight == 0:
            return None
        return round(weighted_sum / total_weight, 2)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "written_weight": self.written_weight,
            "oral_weight": self.oral_weight,
            "grades": [g.to_dict() for g in self.grades],
        }

    @staticmethod
    def from_dict(data: dict) -> "Subject":
        subject = Subject(
            name=data["name"],
            written_weight=data.get("written_weight", 2.0),
            oral_weight=data.get("oral_weight", 1.0),
            id=data.get("id", uuid.uuid4().hex[:8]),
        )
        subject.grades = [Grade.from_dict(g) for g in data.get("grades", [])]
        return subject
