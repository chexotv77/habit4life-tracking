"""
Caso de uso principal (FACADE del componente).

HabitTrackingService expone operaciones de alto nivel y coordina por dentro:
repositorio (puerto), construcción vía Builder/Factory, suscripción de
observadores y delegación de la lógica al dominio. El cliente (controlador
REST, CLI, test) no necesita conocer esa coreografía.

Inversión de dependencias (D de SOLID): recibe HabitRepository y
NotificationPort por constructor; no instancia adaptadores concretos.
"""
from __future__ import annotations

from datetime import date

from ..domain.errors import HabitNotFound
from ..domain.habit import Habit, HabitType
from ..domain.habit_builder import HabitBuilder
from ..ports.habit_repository import HabitRepository
from ..ports.notification_port import NotificationPort
from .observers import NotificationObserver, WeeklySummaryObserver


class HabitTrackingService:
    def __init__(
        self,
        repository: HabitRepository,
        notifier: NotificationPort,
        recipient: str = "user@habit4life.app",
        summary: WeeklySummaryObserver | None = None,
    ) -> None:
        self._repo = repository
        self._notifier = notifier
        self._recipient = recipient
        self._summary = summary or WeeklySummaryObserver()

    @property
    def summary(self) -> WeeklySummaryObserver:
        return self._summary

    def create_habit(
        self,
        habit_id: str,
        name: str,
        habit_type: HabitType,
        goal: float,
        unit: str = "",
        frequency: str = "daily",
        reason: str | None = None,
    ) -> Habit:
        habit = (
            HabitBuilder()
            .with_id(habit_id)
            .named(name)
            .of_type(habit_type)
            .goal(goal, unit)
            .every(frequency)
            .because(reason or "")
            .build()
        )
        # Suscribe los reactores: notificación + resumen semanal.
        habit.subscribe(NotificationObserver(self._notifier, self._recipient))
        habit.subscribe(self._summary)
        self._repo.save(habit)
        return habit

    def _require(self, habit_id: str) -> Habit:
        habit = self._repo.find_by_id(habit_id)
        if habit is None:
            raise HabitNotFound(f"No existe el hábito '{habit_id}'.")
        return habit

    def log_progress(
        self, habit_id: str, amount: float, day: date | None = None
    ) -> int:
        """Registra progreso y devuelve la racha vigente del hábito."""
        habit = self._require(habit_id)
        habit.log_progress(amount, day)
        self._repo.save(habit)
        return habit.current_streak(reference=day)

    def pause_habit(self, habit_id: str) -> None:
        habit = self._require(habit_id)
        habit.pause()
        self._repo.save(habit)

    def resume_habit(self, habit_id: str) -> None:
        habit = self._require(habit_id)
        habit.resume()
        self._repo.save(habit)

    def archive_habit(self, habit_id: str) -> None:
        habit = self._require(habit_id)
        habit.archive()
        self._repo.save(habit)

    def weekly_summary(self) -> dict[str, dict[str, object]]:
        return self._summary.snapshot()
