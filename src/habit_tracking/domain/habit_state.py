"""
Patrón STATE (comportamiento).

Problema de dominio:
    Un hábito tiene un ciclo de vida (Activo, Pausado, Archivado) y en cada
    etapa las acciones permitidas cambian: no se puede registrar progreso en un
    hábito pausado, ni reactivar uno archivado. Resolverlo con
    `if self.estado == ...` dentro de cada método vuelve el código frágil y
    repetido.

Solución:
    Cada estado es una clase que implementa HabitState y sabe qué acciones
    acepta y a qué estado conduce cada una. El Habit (contexto) no tiene
    ningún if de estado: delega en el objeto estado actual.

Tabla de reglas (celda => transición; 'error' => InvalidHabitTransition):

    Estado      log()          pause()     resume()    archive()
    Active      registra       -> Paused   error       -> Archived
    Paused      error          error       -> Active    -> Archived
    Archived    error          error       error        error   (terminal)
"""
from __future__ import annotations

from abc import ABC
from datetime import date
from typing import TYPE_CHECKING

from .errors import InvalidHabitTransition

if TYPE_CHECKING:
    from .habit import Habit, HabitLog


class HabitState(ABC):
    """Rol State: comportamiento por defecto = acción no permitida."""

    name: str = "state"

    def log(self, habit: "Habit", amount: float, day: date) -> "HabitLog":
        raise InvalidHabitTransition(
            f"No se puede registrar progreso en un hábito '{self.name}'."
        )

    def pause(self, habit: "Habit") -> None:
        raise InvalidHabitTransition(
            f"No se puede pausar un hábito '{self.name}'."
        )

    def resume(self, habit: "Habit") -> None:
        raise InvalidHabitTransition(
            f"No se puede reanudar un hábito '{self.name}'."
        )

    def archive(self, habit: "Habit") -> None:
        raise InvalidHabitTransition(
            f"No se puede archivar un hábito '{self.name}'."
        )


class ActiveState(HabitState):
    name = "active"

    def log(self, habit: "Habit", amount: float, day: date) -> "HabitLog":
        return habit._record_log(amount, day)

    def pause(self, habit: "Habit") -> None:
        habit._change_state(PausedState())

    def archive(self, habit: "Habit") -> None:
        habit._change_state(ArchivedState())


class PausedState(HabitState):
    name = "paused"

    def resume(self, habit: "Habit") -> None:
        habit._change_state(ActiveState())

    def archive(self, habit: "Habit") -> None:
        habit._change_state(ArchivedState())


class ArchivedState(HabitState):
    """Estado terminal: no acepta ninguna acción."""

    name = "archived"
