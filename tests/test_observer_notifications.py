"""Pruebas del patrón Observer y de la traducción de los Adapters de notificación."""
from datetime import date, timedelta

from habit_tracking.adapters.notifications.adapters import (
    EmailNotificationAdapter,
    PushNotificationAdapter,
    SmsNotificationAdapter,
)
from habit_tracking.adapters.notifications.providers import (
    FcmClient,
    SmsGateway,
    SmtpServer,
)
from habit_tracking.application.observers import (
    NotificationObserver,
    WeeklySummaryObserver,
)
from habit_tracking.domain.habit import HabitType
from habit_tracking.domain.habit_builder import HabitBuilder
from habit_tracking.ports.notification_port import Notification


def test_cumplir_racha_notifica_y_actualiza_el_resumen():
    fcm = FcmClient()
    push = PushNotificationAdapter(fcm, device_token="tok-123")
    summary = WeeklySummaryObserver()

    habit = (
        HabitBuilder()
        .with_id("h-water")
        .named("Tomar agua")
        .of_type(HabitType.INCREASE)
        .goal(8, "vasos")
        .with_milestones(3)  # hito corto para la prueba
        .build()
    )
    habit.subscribe(NotificationObserver(push, recipient="user@demo.app"))
    habit.subscribe(summary)

    start = date(2026, 10, 1)
    for i in range(3):  # 3 días consecutivos cumpliendo la meta
        habit.log_progress(8, start + timedelta(days=i))

    titles = [s["payload"]["title"] for s in fcm.sent]
    assert any("Racha" in t for t in titles)          # se disparó el hito de racha
    assert sum("Meta" in t for t in titles) == 3       # una por cada día cumplido
    assert summary.days_met("h-water") == 3
    assert summary.best_streak("h-water") == 3


def test_dia_no_cumplido_no_notifica():
    fcm = FcmClient()
    habit = (
        HabitBuilder()
        .with_id("h2")
        .named("Tomar agua")
        .of_type(HabitType.INCREASE)
        .goal(8, "vasos")
        .build()
    )
    habit.subscribe(NotificationObserver(PushNotificationAdapter(fcm, "tok"), "u@d.app"))
    habit.log_progress(3, date(2026, 10, 1))  # 3 < 8 => no cumple
    assert fcm.sent == []


def test_adapters_traducen_a_la_firma_de_cada_proveedor():
    n = Notification(recipient="ana@correo.com", title="Hola", body="Cuerpo")

    smtp = SmtpServer()
    EmailNotificationAdapter(smtp).send(n)
    assert smtp.outbox[0]["to"] == "ana@correo.com"
    assert smtp.outbox[0]["subject"] == "Hola"

    sms_gw = SmsGateway()
    SmsNotificationAdapter(sms_gw).send(Notification("300100", "T", "B"))
    assert sms_gw.log[0]["number"] == "300100"
    assert "T" in sms_gw.log[0]["text"] and "B" in sms_gw.log[0]["text"]
