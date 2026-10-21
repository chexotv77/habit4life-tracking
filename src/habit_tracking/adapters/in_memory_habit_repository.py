"""
Adaptador de persistencia en memoria (sustituye a una base de datos real).

Para este laboratorio no se exige BD real: un repositorio en memoria basta y
mantiene las pruebas rápidas y deterministas.
"""
from __future__ import annotations

from ..domain.habit import Habit
from ..ports.habit_repository import HabitRepository


class InMemoryHabitRepository(HabitRepository):
    def __init__(self) -> None:
        self._store: dict[str, Habit] = {}

    def save(self, habit: Habit) -> None:
        self._store[habit.id] = habit

    def find_by_id(self, habit_id: str) -> Habit | None:
        return self._store.get(habit_id)

    def list_all(self) -> list[Habit]:
        return list(self._store.values())

    def delete(self, habit_id: str) -> None:
        self._store.pop(habit_id, None)
