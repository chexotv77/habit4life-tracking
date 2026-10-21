"""
Pruebas del patrón Strategy e, sobre todo, del principio ABIERTO/CERRADO:
se agrega una estrategia nueva SIN modificar el contexto (Habit) ni las
estrategias existentes.
"""
from datetime import date

from habit_tracking.domain.goal_strategy import (
    GoalEvaluationStrategy,
    IncreaseGoalStrategy,
    MaintainGoalStrategy,
    ReduceGoalStrategy,
)
from habit_tracking.domain.habit import Habit, HabitType


def test_increase_strategy_cumple_al_alcanzar_meta():
    s = IncreaseGoalStrategy()
    assert s.is_met(8, 8) is True
    assert s.is_met(9, 8) is True
    assert s.is_met(7, 8) is False


def test_reduce_strategy_cumple_por_debajo_del_tope():
    s = ReduceGoalStrategy()
    assert s.is_met(120, 120) is True
    assert s.is_met(90, 120) is True
    assert s.is_met(150, 120) is False


def test_maintain_strategy_cumple_dentro_de_la_banda():
    s = MaintainGoalStrategy(tolerance=0.10)  # 8h +/- 10% => [7.2, 8.8]
    assert s.is_met(8, 8) is True
    assert s.is_met(7.5, 8) is True
    assert s.is_met(9, 8) is False


def test_open_closed_nueva_estrategia_sin_tocar_el_contexto():
    """
    Estrategia NUEVA definida aquí mismo: 'cumple solo si el total es cero'
    (para hábitos de abstinencia, p.ej. 'cero cigarrillos'). El contexto Habit
    la acepta sin que haya habido que modificar ninguna clase existente.
    """

    class ZeroIsSuccessStrategy(GoalEvaluationStrategy):
        label = "zero"

        def is_met(self, total, goal):
            return total == 0

        def progress(self, total, goal):
            return 1.0 if total == 0 else 0.0

    habit = Habit(
        habit_id="h-zero",
        name="Cero cigarrillos",
        habit_type=HabitType.REDUCE,
        goal=0,
        unit="unidades",
        frequency="daily",
        goal_strategy=ZeroIsSuccessStrategy(),
    )
    today = date(2026, 10, 20)
    habit.log_progress(0, today)
    assert habit.is_day_met(today) is True

    tomorrow = date(2026, 10, 21)
    habit.log_progress(2, tomorrow)
    assert habit.is_day_met(tomorrow) is False
