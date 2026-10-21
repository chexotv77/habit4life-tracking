"""Excepciones del dominio."""


class DomainError(Exception):
    """Raíz de los errores de negocio del servicio de Habit Tracking."""


class InvalidHabitTransition(DomainError):
    """Se intentó una acción no permitida en el estado actual del hábito."""


class HabitBuildError(DomainError):
    """Datos insuficientes o inconsistentes al construir un hábito."""


class HabitNotFound(DomainError):
    """No existe un hábito con el identificador solicitado."""
