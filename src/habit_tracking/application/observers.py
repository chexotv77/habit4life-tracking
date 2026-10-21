"""
Observadores concretos (parte del patrón OBSERVER).

Son los "reactores" que se suscriben a los eventos que publica cada Habit.
Viven en la capa de aplicación porque traducen eventos de dominio hacia los
puertos (NotificationPort) o hacia estado de aplicación (resumen semanal).
"""
from __future__ import annotations

from ..domain.events import (
    GoalMetEvent,
    HabitEvent,
    HabitObserver,
    StreakMilestoneEvent,
)
from ..ports.notification_port import Notification, NotificationPort


class NotificationObserver(HabitObserver):
    """Al recibir un evento, arma el mensaje y lo envía por el puerto."""

    def __init__(self, notifier: NotificationPort, recipient: str) -> None:
        self._notifier = notifier
        self._recipient = recipient

    def on_event(self, event: HabitEvent) -> None:
        if isinstance(event, StreakMilestoneEvent):
            self._notifier.send(
                Notification(
                    recipient=self._recipient,
                    title="¡Racha desbloqueada! 🔥",
                    body=f"Llevas {event.streak} días seguidos con '{event.habit_name}'.",
                )
            )
        elif isinstance(event, GoalMetEvent):
            self._notifier.send(
                Notification(
                    recipient=self._recipient,
                    title="Meta del día cumplida ✅",
                    body=f"Completaste '{event.habit_name}' hoy. ¡Sigue así!",
                )
            )


class WeeklySummaryObserver(HabitObserver):
    """
    Acumula estadísticas que alimentan la pantalla 'Weekly Summary'
    (días cumplidos por hábito, mejor racha). Demuestra que a un mismo evento
    pueden reaccionar varios observadores sin que el Habit los conozca.
    """

    def __init__(self) -> None:
        self._days_met: dict[str, int] = {}
        self._best_streak: dict[str, int] = {}
        self._names: dict[str, str] = {}

    def on_event(self, event: HabitEvent) -> None:
        self._names[event.habit_id] = event.habit_name
        if isinstance(event, GoalMetEvent):
            self._days_met[event.habit_id] = self._days_met.get(event.habit_id, 0) + 1
        elif isinstance(event, StreakMilestoneEvent):
            self._best_streak[event.habit_id] = max(
                self._best_streak.get(event.habit_id, 0), event.streak
            )

    def days_met(self, habit_id: str) -> int:
        return self._days_met.get(habit_id, 0)

    def best_streak(self, habit_id: str) -> int:
        return self._best_streak.get(habit_id, 0)

    def snapshot(self) -> dict[str, dict[str, object]]:
        return {
            habit_id: {
                "name": self._names.get(habit_id, habit_id),
                "days_met": self._days_met.get(habit_id, 0),
                "best_streak": self._best_streak.get(habit_id, 0),
            }
            for habit_id in self._names
        }
