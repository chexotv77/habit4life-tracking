"""
Evidencia ejecutable (Fase 6) + Prueba de evolución (Fase 7).

Correr con:  python demo.py

Muestra primero el flujo normal del componente y luego los TRES escenarios
de cambio, evidenciando que cada uno se resuelve AGREGANDO clases, sin
modificar el núcleo ni las clases existentes (gracias a SOLID + patrones).
"""
import os
import sys
from datetime import date, timedelta

# Permite ejecutar `python demo.py` sin instalar el paquete: añade src/ al path.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from habit_tracking.adapters.in_memory_habit_repository import InMemoryHabitRepository
from habit_tracking.adapters.notifications.adapters import PushNotificationAdapter
from habit_tracking.adapters.notifications.providers import FcmClient
from habit_tracking.adapters.repository_decorators import (
    CachingHabitRepository,
    LoggingHabitRepository,
)
from habit_tracking.application.habit_service import HabitTrackingService
from habit_tracking.application.observers import NotificationObserver
from habit_tracking.domain.goal_strategy import GoalEvaluationStrategy
from habit_tracking.domain.habit import Habit, HabitType
from habit_tracking.domain.habit_builder import HabitBuilder
from habit_tracking.domain.habit_state import ActiveState, HabitState
from habit_tracking.ports.notification_port import Notification, NotificationPort


def banner(text: str) -> None:
    print("\n" + "=" * 62 + f"\n {text}\n" + "=" * 62)


def flujo_normal() -> None:
    banner("FLUJO NORMAL DEL COMPONENTE")
    repo = CachingHabitRepository(LoggingHabitRepository(InMemoryHabitRepository()))
    fcm = FcmClient()
    service = HabitTrackingService(
        repo, PushNotificationAdapter(fcm, "device-xyz"), recipient="ana@demo.app"
    )

    service.create_habit("water", "Tomar agua", HabitType.INCREASE, 8, "vasos")
    print("Hábito creado:", repo.find_by_id("water"))

    start = date(2026, 10, 1)
    for i in range(7):  # una semana cumpliendo la meta -> hito de racha (7)
        streak = service.log_progress("water", 8, start + timedelta(days=i))
    print(f"Racha tras 7 días: {streak}")
    print("Notificaciones push enviadas:", len(fcm.sent))
    print("Resumen semanal:", service.weekly_summary())


def escenario_1_nuevo_canal() -> None:
    banner("EVOLUCIÓN 1: nuevo canal de notificación (WhatsApp)")

    # --- SOLO se agregan estas dos clases; el núcleo no se toca. ---
    class WhatsAppGateway:  # proveedor externo con su propia firma
        def __init__(self):
            self.messages = []

        def post_message(self, to, template):
            self.messages.append((to, template))

    class WhatsAppAdapter(NotificationPort):  # Adapter -> implementa el puerto
        def __init__(self, gateway):
            self._gateway = gateway

        def send(self, notification: Notification) -> None:
            self._gateway.post_message(
                notification.recipient, f"{notification.title}: {notification.body}"
            )

    gw = WhatsAppGateway()
    habit = (
        HabitBuilder().with_id("gym").named("Ir al gym").of_type(HabitType.INCREASE)
        .goal(1, "sesión").with_milestones(1).build()
    )
    habit.subscribe(NotificationObserver(WhatsAppAdapter(gw), "+57300..."))
    habit.log_progress(1, date(2026, 10, 1))
    print("Mensajes de WhatsApp recibidos:", gw.messages)
    print("-> Clases nuevas: WhatsAppGateway, WhatsAppAdapter. Núcleo modificado: 0")


def escenario_2_nueva_regla() -> None:
    banner("EVOLUCIÓN 2: nueva regla de meta (abstinencia: 'cero')")

    # --- SOLO se agrega esta Strategy; Habit (contexto) no cambia. ---
    class ZeroIsSuccessStrategy(GoalEvaluationStrategy):
        label = "zero"

        def is_met(self, total, goal):
            return total == 0

        def progress(self, total, goal):
            return 1.0 if total == 0 else 0.0

    habit = Habit(
        "nosmoke", "Cero cigarrillos", HabitType.REDUCE, 0, "unid", "daily",
        goal_strategy=ZeroIsSuccessStrategy(),
    )
    habit.log_progress(0, date(2026, 10, 1))
    print("Día con 0 cigarrillos, ¿cumple?:", habit.is_day_met(date(2026, 10, 1)))
    habit.log_progress(3, date(2026, 10, 2))
    print("Día con 3 cigarrillos, ¿cumple?:", habit.is_day_met(date(2026, 10, 2)))
    print("-> Clase nueva: ZeroIsSuccessStrategy. Habit/otras estrategias modificadas: 0")


def escenario_3_nuevo_estado() -> None:
    banner("EVOLUCIÓN 3: nuevo estado del ciclo de vida (Snoozed)")

    # --- SOLO se agrega esta clase State; Habit y los demás estados no cambian. ---
    class SnoozedState(HabitState):
        name = "snoozed"

        def resume(self, habit):
            habit._change_state(ActiveState())

    habit = (
        HabitBuilder().with_id("read").named("Leer").of_type(HabitType.INCREASE)
        .goal(20, "min").build()
    )
    habit._change_state(SnoozedState())  # en producción: un método snooze()
    print("Estado:", habit.state_name)
    try:
        habit.log_progress(10, date(2026, 10, 1))
    except Exception as exc:
        print("Registrar en Snoozed ->", type(exc).__name__)
    habit.resume()
    print("Tras resume ->", habit.state_name)
    print("-> Clase nueva: SnoozedState. Habit/otros estados modificados: 0")


if __name__ == "__main__":
    flujo_normal()
    escenario_1_nuevo_canal()
    escenario_2_nueva_regla()
    escenario_3_nuevo_estado()
    print("\nListo. Los tres cambios se resolvieron agregando clases, no modificándolas.")
