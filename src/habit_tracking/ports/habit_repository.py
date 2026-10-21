"""Puerto de salida: persistencia de hábitos."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..domain.habit import Habit


class HabitRepository(ABC):
    """
    Interfaz pequeña y cohesionada (I de SOLID: segregación de interfaces).
    El caso de uso depende de esto, no de una base de datos concreta.
    """

    @abstractmethod
    def save(self, habit: Habit) -> None: ...

    @abstractmethod
    def find_by_id(self, habit_id: str) -> Habit | None: ...

    @abstractmethod
    def list_all(self) -> list[Habit]: ...

    @abstractmethod
    def delete(self, habit_id: str) -> None: ...
