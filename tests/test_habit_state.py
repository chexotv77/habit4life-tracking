"""Pruebas del patrón State: transiciones válidas e inválidas del ciclo de vida."""
from datetime import date

import pytest

from habit_tracking.domain.errors import InvalidHabitTransition
from habit_tracking.domain.habit import HabitType
from habit_tracking.domain.habit_builder import HabitBuilder


def _build_habit():
    return (
        HabitBuilder()
        .with_id("h1")
        .named("Tomar agua")
        .of_type(HabitType.INCREASE)
        .goal(8, "vasos")
        .build()
    )


def test_hilo_de_vida_normal():
    habit = _build_habit()
    assert habit.state_name == "active"
    habit.pause()
    assert habit.state_name == "paused"
    habit.resume()
    assert habit.state_name == "active"
    habit.archive()
    assert habit.state_name == "archived"


def test_no_se_puede_registrar_en_pausado():
    habit = _build_habit()
    habit.pause()
    with pytest.raises(InvalidHabitTransition):
        habit.log_progress(3, date(2026, 10, 20))


def test_archivado_es_terminal():
    habit = _build_habit()
    habit.archive()
    with pytest.raises(InvalidHabitTransition):
        habit.log_progress(1, date(2026, 10, 20))
    with pytest.raises(InvalidHabitTransition):
        habit.resume()


def test_reanudar_un_hilo_activo_es_invalido():
    habit = _build_habit()
    with pytest.raises(InvalidHabitTransition):
        habit.resume()
