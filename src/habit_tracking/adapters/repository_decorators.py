"""
Patrón DECORATOR (estructural).

Problema de dominio:
    Queremos agregar caché (para no releer el mismo hábito una y otra vez al
    pintar la pantalla "Today") y auditoría (registrar cada acceso) SIN tocar
    el repositorio concreto ni ensuciar la lógica de dominio.

Solución:
    Cada decorador implementa el MISMO puerto HabitRepository y envuelve otro
    HabitRepository. Como respetan la interfaz, se pueden apilar en cualquier
    orden (Liskov): Caching(Logging(InMemory())). El cliente sigue viendo
    "un HabitRepository" y no se entera.
"""
from __future__ import annotations

from ..domain.habit import Habit
from ..ports.habit_repository import HabitRepository


class _RepositoryDecorator(HabitRepository):
    """Base de decoradores: delega todo en el repositorio envuelto."""

    def __init__(self, inner: HabitRepository) -> None:
        self._inner = inner

    def save(self, habit: Habit) -> None:
        self._inner.save(habit)

    def find_by_id(self, habit_id: str) -> Habit | None:
        return self._inner.find_by_id(habit_id)

    def list_all(self) -> list[Habit]:
        return self._inner.list_all()

    def delete(self, habit_id: str) -> None:
        self._inner.delete(habit_id)


class CachingHabitRepository(_RepositoryDecorator):
    """Cachea find_by_id; invalida la entrada al guardar o borrar."""

    def __init__(self, inner: HabitRepository) -> None:
        super().__init__(inner)
        self._cache: dict[str, Habit] = {}
        self.hits = 0
        self.misses = 0

    def find_by_id(self, habit_id: str) -> Habit | None:
        if habit_id in self._cache:
            self.hits += 1
            return self._cache[habit_id]
        self.misses += 1
        habit = self._inner.find_by_id(habit_id)
        if habit is not None:
            self._cache[habit_id] = habit
        return habit

    def save(self, habit: Habit) -> None:
        self._inner.save(habit)
        self._cache[habit.id] = habit  # mantiene la caché coherente

    def delete(self, habit_id: str) -> None:
        self._inner.delete(habit_id)
        self._cache.pop(habit_id, None)


class LoggingHabitRepository(_RepositoryDecorator):
    """Registra (audita) cada operación sin alterar el comportamiento."""

    def __init__(self, inner: HabitRepository) -> None:
        super().__init__(inner)
        self.audit: list[str] = []

    def save(self, habit: Habit) -> None:
        self.audit.append(f"save:{habit.id}")
        super().save(habit)

    def find_by_id(self, habit_id: str) -> Habit | None:
        self.audit.append(f"find:{habit_id}")
        return super().find_by_id(habit_id)

    def delete(self, habit_id: str) -> None:
        self.audit.append(f"delete:{habit_id}")
        super().delete(habit_id)
