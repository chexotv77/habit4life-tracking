"""
Entidad raíz del dominio: Habit.

Habit es el CONTEXTO de dos patrones de comportamiento:
  * STATE    -> su ciclo de vida (Active/Paused/Archived) vive en habit_state.
  * STRATEGY -> la regla para decidir si un día cumple la meta vive en
                goal_strategy; Habit solo conoce la abstracción.
Y es el SUBJECT del patrón OBSERVER a través de HabitEventPublisher.

Responsabilidad única (S de SOLID): representar un hábito y las reglas de
negocio que lo gobiernan. No sabe de bases de datos, HTTP ni notificaciones:
eso vive en los adaptadores.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum

from .errors import DomainError
from .events import GoalMetEvent, HabitEventPublisher, HabitObserver, StreakMilestoneEvent
from .goal_strategy import GoalEvaluationStrategy
from .habit_state import ActiveState, HabitState

DEFAULT_MILESTONES: tuple[int, ...] = (7, 30, 100)


class HabitType(str, Enum):
    INCREASE = "increase"
    MAINTAIN = "maintain"
    REDUCE = "reduce"


@dataclass(frozen=True)
class HabitLog:
    """Un registro de progreso en un día dado (value object inmutable)."""

    day: date
    amount: float


class Habit:
    def __init__(
        self,
        habit_id: str,
        name: str,
        habit_type: HabitType,
        goal: float,
        unit: str,
        frequency: str,
        goal_strategy: GoalEvaluationStrategy,
        reason: str | None = None,
        publisher: HabitEventPublisher | None = None,
        milestones: tuple[int, ...] = DEFAULT_MILESTONES,
    ) -> None:
        if not name:
            raise DomainError("El hábito necesita un nombre.")
        self._id = habit_id
        self._name = name
        self._type = habit_type
        self._goal = goal
        self._unit = unit
        self._frequency = frequency
        self._strategy = goal_strategy
        self._reason = reason
        self._state: HabitState = ActiveState()
        self._logs: list[HabitLog] = []
        self._publisher = publisher or HabitEventPublisher()
        self._milestones = tuple(sorted(milestones))
        self._notified_milestones: set[int] = set()

    # ---- identidad / lectura -------------------------------------------------
    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def habit_type(self) -> HabitType:
        return self._type

    @property
    def goal(self) -> float:
        return self._goal

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def frequency(self) -> str:
        return self._frequency

    @property
    def reason(self) -> str | None:
        return self._reason

    @property
    def strategy(self) -> GoalEvaluationStrategy:
        return self._strategy

    @property
    def state_name(self) -> str:
        return self._state.name

    @property
    def logs(self) -> list[HabitLog]:
        return list(self._logs)

    # ---- suscripción al Observer --------------------------------------------
    def subscribe(self, observer: HabitObserver) -> None:
        self._publisher.subscribe(observer)

    def unsubscribe(self, observer: HabitObserver) -> None:
        self._publisher.unsubscribe(observer)

    # ---- acciones (delegan en el STATE actual) ------------------------------
    def log_progress(self, amount: float, day: date | None = None) -> HabitLog:
        return self._state.log(self, amount, day or date.today())

    def pause(self) -> None:
        self._state.pause(self)

    def resume(self) -> None:
        self._state.resume(self)

    def archive(self) -> None:
        self._state.archive(self)

    # ---- métricas de negocio -------------------------------------------------
    def day_total(self, day: date) -> float:
        return sum(log.amount for log in self._logs if log.day == day)

    def is_day_met(self, day: date) -> bool:
        return self._strategy.is_met(self.day_total(day), self._goal)

    def progress_today(self, day: date | None = None) -> float:
        day = day or date.today()
        return self._strategy.progress(self.day_total(day), self._goal)

    def current_streak(self, reference: date | None = None) -> int:
        """
        Días consecutivos CON REGISTRO que cumplieron la meta, contando hacia
        atrás desde `reference`. Un día sin ningún registro corta la racha
        (no se asume engagement en días vacíos).
        """
        if not self._logs:
            return 0
        logged_days = {log.day for log in self._logs}
        reference = reference or max(logged_days)
        streak = 0
        cursor = reference
        while cursor in logged_days and self.is_day_met(cursor):
            streak += 1
            cursor = cursor - timedelta(days=1)
        return streak

    # ---- API interna usada por los objetos State ----------------------------
    def _change_state(self, new_state: HabitState) -> None:
        self._state = new_state

    def _record_log(self, amount: float, day: date) -> HabitLog:
        log = HabitLog(day=day, amount=amount)
        self._logs.append(log)
        if self.is_day_met(day):
            self._publisher.publish(
                GoalMetEvent(
                    habit_id=self._id,
                    habit_name=self._name,
                    day=day,
                    total=self.day_total(day),
                )
            )
            self._check_streak_milestone(day)
        return log

    def _check_streak_milestone(self, day: date) -> None:
        streak = self.current_streak(reference=day)
        for milestone in self._milestones:
            if streak >= milestone and milestone not in self._notified_milestones:
                self._notified_milestones.add(milestone)
                self._publisher.publish(
                    StreakMilestoneEvent(
                        habit_id=self._id,
                        habit_name=self._name,
                        streak=milestone,
                    )
                )

    def __repr__(self) -> str:  # pragma: no cover - ayuda en el demo
        return (
            f"Habit(id={self._id!r}, name={self._name!r}, "
            f"type={self._type.value}, state={self._state.name})"
        )
