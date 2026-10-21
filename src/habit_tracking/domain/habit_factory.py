"""
Patrón FACTORY METHOD (creacional).

Problema de dominio:
    Crear un hábito implica además elegir la política de evaluación correcta
    (Strategy) según su tipo. Si eso se hace con `new`/if dispersos por el
    código, cada tipo nuevo se filtra en muchos lugares.

Solución:
    Un creador abstracto (HabitCreator) define el método fábrica
    `_create_strategy()` que cada subclase concreta implementa para devolver
    la estrategia que le corresponde, y arma el Habit ya configurado. La
    subclase decide el producto concreto; el resto del sistema solo pide
    "créame un hábito de tipo X".
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .events import HabitEventPublisher
from .goal_strategy import (
    GoalEvaluationStrategy,
    IncreaseGoalStrategy,
    MaintainGoalStrategy,
    ReduceGoalStrategy,
)
from .habit import DEFAULT_MILESTONES, Habit, HabitType


class HabitCreator(ABC):
    """Rol Creator: define el método fábrica y el armado común del hábito."""

    @abstractmethod
    def _create_strategy(self) -> GoalEvaluationStrategy:
        """Método fábrica: la subclase decide la estrategia concreta."""

    @abstractmethod
    def _habit_type(self) -> HabitType: ...

    def new_habit(
        self,
        habit_id: str,
        name: str,
        goal: float,
        unit: str,
        frequency: str,
        reason: str | None = None,
        publisher: HabitEventPublisher | None = None,
        milestones: tuple[int, ...] = DEFAULT_MILESTONES,
    ) -> Habit:
        return Habit(
            habit_id=habit_id,
            name=name,
            habit_type=self._habit_type(),
            goal=goal,
            unit=unit,
            frequency=frequency,
            goal_strategy=self._create_strategy(),
            reason=reason,
            publisher=publisher,
            milestones=milestones,
        )


class IncreaseHabitCreator(HabitCreator):
    def _create_strategy(self) -> GoalEvaluationStrategy:
        return IncreaseGoalStrategy()

    def _habit_type(self) -> HabitType:
        return HabitType.INCREASE


class MaintainHabitCreator(HabitCreator):
    def __init__(self, tolerance: float = 0.10) -> None:
        self._tolerance = tolerance

    def _create_strategy(self) -> GoalEvaluationStrategy:
        return MaintainGoalStrategy(tolerance=self._tolerance)

    def _habit_type(self) -> HabitType:
        return HabitType.MAINTAIN


class ReduceHabitCreator(HabitCreator):
    def _create_strategy(self) -> GoalEvaluationStrategy:
        return ReduceGoalStrategy()

    def _habit_type(self) -> HabitType:
        return HabitType.REDUCE


# Selector de creador por tipo. Vive en un solo lugar: extender el sistema con
# un tipo nuevo es registrar una entrada aquí, sin tocar al resto.
_CREATORS: dict[HabitType, HabitCreator] = {
    HabitType.INCREASE: IncreaseHabitCreator(),
    HabitType.MAINTAIN: MaintainHabitCreator(),
    HabitType.REDUCE: ReduceHabitCreator(),
}


def creator_for(habit_type: HabitType) -> HabitCreator:
    try:
        return _CREATORS[habit_type]
    except KeyError:  # pragma: no cover - defensivo
        raise ValueError(f"Tipo de hábito no soportado: {habit_type}")
