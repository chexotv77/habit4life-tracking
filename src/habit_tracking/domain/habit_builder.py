"""
Patrón BUILDER (creacional).

Problema de dominio:
    La pantalla "Create Habit" captura muchos datos, varios opcionales
    (nombre, tipo, meta, unidad, frecuencia, motivo, hitos de racha...).
    Un constructor con 8 parámetros posicionales es ilegible y propenso a
    errores ("¿este número era la meta o la tolerancia?").

Solución:
    Un HabitBuilder arma el hábito paso a paso con una API fluida y validando
    al final. En build() delega la creación del producto al FACTORY METHOD
    correspondiente al tipo -> cada patrón creacional cubre una preocupación
    distinta (Builder: ensamblar datos; Factory Method: elegir configuración
    por tipo) sin pisarse.
"""
from __future__ import annotations

from .errors import HabitBuildError
from .events import HabitEventPublisher
from .habit import DEFAULT_MILESTONES, Habit, HabitType
from .habit_factory import creator_for


class HabitBuilder:
    def __init__(self) -> None:
        self._id: str | None = None
        self._name: str | None = None
        self._type: HabitType | None = None
        self._goal: float | None = None
        self._unit: str = ""
        self._frequency: str = "daily"
        self._reason: str | None = None
        self._publisher: HabitEventPublisher | None = None
        self._milestones: tuple[int, ...] = DEFAULT_MILESTONES

    def with_id(self, habit_id: str) -> "HabitBuilder":
        self._id = habit_id
        return self

    def named(self, name: str) -> "HabitBuilder":
        self._name = name
        return self

    def of_type(self, habit_type: HabitType) -> "HabitBuilder":
        self._type = habit_type
        return self

    def goal(self, goal: float, unit: str = "") -> "HabitBuilder":
        self._goal = goal
        if unit:
            self._unit = unit
        return self

    def measured_in(self, unit: str) -> "HabitBuilder":
        self._unit = unit
        return self

    def every(self, frequency: str) -> "HabitBuilder":
        self._frequency = frequency
        return self

    def because(self, reason: str) -> "HabitBuilder":
        self._reason = reason
        return self

    def with_milestones(self, *milestones: int) -> "HabitBuilder":
        if milestones:
            self._milestones = tuple(milestones)
        return self

    def publishing_to(self, publisher: HabitEventPublisher) -> "HabitBuilder":
        self._publisher = publisher
        return self

    def build(self) -> Habit:
        missing = [
            field
            for field, value in (
                ("id", self._id),
                ("name", self._name),
                ("type", self._type),
                ("goal", self._goal),
            )
            if value is None
        ]
        if missing:
            raise HabitBuildError(f"Faltan datos obligatorios: {', '.join(missing)}")

        creator = creator_for(self._type)  # type: ignore[arg-type]
        return creator.new_habit(
            habit_id=self._id,  # type: ignore[arg-type]
            name=self._name,  # type: ignore[arg-type]
            goal=self._goal,  # type: ignore[arg-type]
            unit=self._unit,
            frequency=self._frequency,
            reason=self._reason,
            publisher=self._publisher,
            milestones=self._milestones,
        )
