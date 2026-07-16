"""Notenrechner: berechnet, welche Note als nächstes nötig ist,
um einen Zielschnitt zu erreichen."""

from __future__ import annotations

from .models import Subject


def required_grade(subject: Subject, target_average: float, next_grade_type: str) -> float | None:
    """Berechnet welche Note (next_grade_type) nötig ist, um target_average zu erreichen.

    Gibt None zurück, wenn das Ziel mit einer gültigen Note (1-6) nicht erreichbar ist.
    """
    written = [g.value for g in subject.grades if g.grade_type == "schriftlich"]
    oral = [g.value for g in subject.grades if g.grade_type == "muendlich"]

    if next_grade_type == "schriftlich":
        written = written + ["X"]
    else:
        oral = oral + ["X"]

    # Wir lösen die gewichtete Durchschnittsformel nach X auf.
    w_weight = subject.written_weight
    o_weight = subject.oral_weight

    def partial_sum_and_weight(values: list, weight: float) -> tuple[float, float, int]:
        known = [v for v in values if v != "X"]
        has_x = "X" in values
        n = len(values)
        if n == 0:
            return 0.0, 0.0, 0
        if has_x:
            # Kategorie-Beitrag = weight * (sum(known) + X) / n
            #                   = (weight/n)*sum(known) + (weight/n)*X
            factor = weight / n
            return factor * sum(known), factor, n
        avg = sum(known) / n
        return avg * weight, 0.0, n

    w_const, w_x_coef, w_n = partial_sum_and_weight(written, w_weight)
    o_const, o_x_coef, o_n = partial_sum_and_weight(oral, o_weight)

    total_weight = 0.0
    if w_n:
        total_weight += w_weight
    if o_n:
        total_weight += o_weight

    if total_weight == 0:
        return None

    # target = (w_const + w_x_coef * X + o_const + o_x_coef * X) / total_weight
    x_coef = w_x_coef + o_x_coef
    const = w_const + o_const

    if x_coef == 0:
        return None  # next_grade_type trägt gar nicht zum Schnitt bei (Gewicht 0)

    x = (target_average * total_weight - const) / x_coef
    return round(x, 2)


def is_achievable(value: float) -> bool:
    """Deutsches Notensystem: 1 (beste) bis 6 (schlechteste)."""
    return 1.0 <= value <= 6.0
