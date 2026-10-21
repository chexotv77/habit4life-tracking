"""
Patrón ADAPTER (estructural).

Problema de dominio:
    El núcleo solo sabe "enviar una Notification" (NotificationPort). Pero cada
    proveedor real (push/FCM, email/SMTP, SMS) expone una interfaz distinta e
    incompatible. No queremos que el dominio dependa de ninguna de ellas.

Solución:
    Un adaptador por proveedor implementa NotificationPort y traduce la
    llamada uniforme `send(notification)` a la firma propia del proveedor.
    Agregar un canal nuevo = agregar un adaptador, sin tocar el núcleo
    (Abierto/Cerrado + inversión de dependencias).
"""
from __future__ import annotations

from ...ports.notification_port import Notification, NotificationPort
from .providers import FcmClient, SmsGateway, SmtpServer


class PushNotificationAdapter(NotificationPort):
    def __init__(self, client: FcmClient, device_token: str) -> None:
        self._client = client
        self._device_token = device_token

    def send(self, notification: Notification) -> None:
        self._client.dispatch(
            self._device_token,
            {"title": notification.title, "body": notification.body},
        )


class EmailNotificationAdapter(NotificationPort):
    def __init__(self, server: SmtpServer) -> None:
        self._server = server

    def send(self, notification: Notification) -> None:
        self._server.send_mail(
            notification.recipient,
            notification.title,
            f"<p>{notification.body}</p>",
        )


class SmsNotificationAdapter(NotificationPort):
    def __init__(self, gateway: SmsGateway) -> None:
        self._gateway = gateway

    def send(self, notification: Notification) -> None:
        self._gateway.send_text(
            notification.recipient,
            f"{notification.title} — {notification.body}",
        )
