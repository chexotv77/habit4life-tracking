"""
Patrón OBSERVER (comportamiento).

Problema de dominio:
    Cuando el usuario cumple la meta del día o encadena una racha (streak de
    7, 30... días) hay que reaccionar en varios frentes: enviar una
    notificación de felicitación, actualizar el Resumen Semanal y, a futuro,
    otorgar insignias. Si el Habit llamara directamente a cada uno quedaría
    acoplado a todos ellos y agregar un reactor nuevo obligaría a modificarlo.

Solución:
    El Habit publica eventos a través de un HabitEventPublisher; los
    interesados se suscriben implementando HabitObserver. El publicador no
    sabe quién lo escucha -> bajo acoplamiento y Abierto/Cerrado.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # evita import circular; solo para type hints
    from .habit import Habit


@dataclass(frozen=True)
class HabitEvent:
    """Evento base del dominio."""

    habit_id: str
    habit_name: str


@dataclass(frozen=True)
class GoalMetEvent(HabitEvent):
    """Se cumplió la meta de un día concreto."""

    day: date
    total: float


@dataclass(frozen=True)
class StreakMilestoneEvent(HabitEvent):
    """Se alcanzó una racha hito (7, 30, 100... días consecutivos)."""

    streak: int


class HabitObserver(ABC):
    """Rol Observer: reacciona a eventos sin que el publicador lo conozca."""

    @abstractmethod
    def on_event(self, event: HabitEvent) -> None: ...


class HabitEventPublisher:
    """Rol Subject/Publisher: mantiene la lista de observadores y notifica."""

    def __init__(self) -> None:
        self._observers: list[HabitObserver] = []

    def subscribe(self, observer: HabitObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe(self, observer: HabitObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def publish(self, event: HabitEvent) -> None:
        # Copia defensiva: un observador podría des-suscribirse al reaccionar.
        for observer in list(self._observers):
            observer.on_event(event)
