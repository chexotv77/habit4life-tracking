"""
Prueba de integración del caso de uso (Facade) con el repositorio decorado
(Decorator: Caching(Logging(InMemory))) y un adaptador de notificación real.
"""
from datetime import date

import pytest

from habit_tracking.adapters.in_memory_habit_repository import InMemoryHabitRepository
from habit_tracking.adapters.notifications.adapters import EmailNotificationAdapter
from habit_tracking.adapters.notifications.providers import SmtpServer
from habit_tracking.adapters.repository_decorators import (
    CachingHabitRepository,
    LoggingHabitRepository,
)
from habit_tracking.application.habit_service import HabitTrackingService
from habit_tracking.domain.errors import InvalidHabitTransition
from habit_tracking.domain.habit import HabitType


def _wire():
    base = InMemoryHabitRepository()
    logging = LoggingHabitRepository(base)
    caching = CachingHabitRepository(logging)
    smtp = SmtpServer()
    notifier = EmailNotificationAdapter(smtp)
    service = HabitTrackingService(caching, notifier, recipient="ana@correo.com")
    return service, caching, logging, smtp


def test_flujo_crear_y_registrar_progreso():
    service, caching, logging, smtp = _wire()
    service.create_habit("h-water", "Tomar agua", HabitType.INCREASE, goal=8, unit="vasos")

    streak = service.log_progress("h-water", 8, date(2026, 10, 1))
    assert streak == 1
    assert len(smtp.outbox) == 1  # notificó la meta cumplida por email
    assert service.weekly_summary()["h-water"]["days_met"] == 1


def test_el_decorator_de_cache_funciona():
    service, caching, logging, smtp = _wire()
    service.create_habit("h-read", "Leer", HabitType.INCREASE, goal=20, unit="min")
    service.log_progress("h-read", 20, date(2026, 10, 1))
    service.log_progress("h-read", 20, date(2026, 10, 2))
    # Tras el primer acceso, los find_by_id siguientes salen de la caché.
    assert caching.hits >= 1
    # El decorator de auditoría registró las operaciones sin alterar el flujo.
    assert any(entry.startswith("save:h-read") for entry in logging.audit)


def test_no_se_registra_en_un_habito_pausado():
    service, *_ = _wire()
    service.create_habit("h-gym", "Ir al gym", HabitType.INCREASE, goal=1, unit="sesión")
    service.pause_habit("h-gym")
    with pytest.raises(InvalidHabitTransition):
        service.log_progress("h-gym", 1, date(2026, 10, 1))
