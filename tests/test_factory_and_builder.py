"""Pruebas de los patrones creacionales: Factory Method y Builder."""
import pytest

from habit_tracking.domain.errors import HabitBuildError
from habit_tracking.domain.goal_strategy import (
    IncreaseGoalStrategy,
    MaintainGoalStrategy,
    ReduceGoalStrategy,
)
from habit_tracking.domain.habit import HabitType
from habit_tracking.domain.habit_builder import HabitBuilder
from habit_tracking.domain.habit_factory import (
    IncreaseHabitCreator,
    creator_for,
)


def test_factory_method_devuelve_la_estrategia_correcta_por_tipo():
    casos = {
        HabitType.INCREASE: IncreaseGoalStrategy,
        HabitType.MAINTAIN: MaintainGoalStrategy,
        HabitType.REDUCE: ReduceGoalStrategy,
    }
    for habit_type, expected_strategy in casos.items():
        creator = creator_for(habit_type)
        habit = creator.new_habit("id", "n", goal=5, unit="u", frequency="daily")
        assert habit.habit_type == habit_type
        assert isinstance(habit.strategy, expected_strategy)


def test_creator_concreto_puede_usarse_directo():
    habit = IncreaseHabitCreator().new_habit("id", "Leer", goal=20, unit="min", frequency="daily")
    assert isinstance(habit.strategy, IncreaseGoalStrategy)


def test_builder_fluido_arma_el_habito_completo():
    habit = (
        HabitBuilder()
        .with_id("h-read")
        .named("Leer")
        .of_type(HabitType.INCREASE)
        .goal(20, "min")
        .every("daily")
        .because("Aprender sin trasnochar")
        .with_milestones(3, 7)
        .build()
    )
    assert habit.id == "h-read"
    assert habit.name == "Leer"
    assert habit.goal == 20
    assert habit.unit == "min"
    assert habit.reason == "Aprender sin trasnochar"
    assert isinstance(habit.strategy, IncreaseGoalStrategy)


def test_builder_falla_si_faltan_datos_obligatorios():
    with pytest.raises(HabitBuildError):
        HabitBuilder().named("Sin id ni tipo ni meta").build()
