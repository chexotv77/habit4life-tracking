"""
Patrón STRATEGY (comportamiento).

Problema de dominio:
    "¿El usuario cumplió la meta de hoy?" se responde distinto según el tipo
    de hábito: un hábito de AUMENTAR (tomar >= 8 vasos de agua) se evalúa al
    revés que uno de REDUCIR (usar <= 120 min de redes) o uno de MANTENER
    (dormir ~8 h, dentro de una banda de tolerancia).

    Si esa decisión vive en un switch / if-elif sobre el tipo, cada tipo nuevo
    obliga a modificar el mismo método -> se viola el principio Abierto/Cerrado.

Solución:
    Encapsular cada regla de evaluación detrás de una interfaz común
    (GoalEvaluationStrategy). El Habit (contexto) solo conoce la abstracción;
    agregar una regla nueva es crear UNA clase más, sin tocar nada existente.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class GoalEvaluationStrategy(ABC):
    """Rol Strategy: regla intercambiable para decidir si un día cumple la meta."""

    @abstractmethod
    def is_met(self, total: float, goal: float) -> bool:
        """True si el total acumulado del día satisface la meta."""

    @abstractmethod
    def progress(self, total: float, goal: float) -> float:
        """Avance normalizado [0.0, 1.0] para barras de progreso en la UI."""

    @property
    @abstractmethod
    def label(self) -> str:
        """Nombre legible de la política, útil para logs y reportes."""


class IncreaseGoalStrategy(GoalEvaluationStrategy):
    """Cumple cuando se alcanza o supera la meta (ej.: >= 8 vasos de agua)."""

    label = "increase"

    def is_met(self, total: float, goal: float) -> bool:
        return total >= goal

    def progress(self, total: float, goal: float) -> float:
        if goal <= 0:
            return 1.0
        return min(total / goal, 1.0)


class ReduceGoalStrategy(GoalEvaluationStrategy):
    """Cumple cuando se queda igual o por debajo del tope (ej.: <= 120 min)."""

    label = "reduce"

    def is_met(self, total: float, goal: float) -> bool:
        return total <= goal

    def progress(self, total: float, goal: float) -> float:
        if goal <= 0:
            return 1.0 if total <= 0 else 0.0
        # Cuanto menos se consume, mayor el avance; se topa en [0, 1].
        return max(0.0, min(1.0, (goal - total) / goal + 1.0)) if total > goal else 1.0


class MaintainGoalStrategy(GoalEvaluationStrategy):
    """
    Cumple dentro de una banda de tolerancia alrededor de la meta
    (ej.: dormir 8 h +/- 10%). La tolerancia es configurable por instancia.
    """

    label = "maintain"

    def __init__(self, tolerance: float = 0.10) -> None:
        if not 0 <= tolerance < 1:
            raise ValueError("tolerance debe estar en [0, 1)")
        self._tolerance = tolerance

    def _band(self, goal: float) -> tuple[float, float]:
        margin = goal * self._tolerance
        return goal - margin, goal + margin

    def is_met(self, total: float, goal: float) -> bool:
        low, high = self._band(goal)
        return low <= total <= high

    def progress(self, total: float, goal: float) -> float:
        if goal <= 0:
            return 1.0
        low, high = self._band(goal)
        if low <= total <= high:
            return 1.0
        # Avance proporcional a qué tan cerca está de entrar en la banda.
        nearest = low if total < low else high
        return max(0.0, 1.0 - abs(total - nearest) / goal)
