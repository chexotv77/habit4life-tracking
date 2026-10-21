"""Puerto de salida: envío de notificaciones."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Notification:
    recipient: str
    title: str
    body: str


class NotificationPort(ABC):
    """
    Una sola operación: el núcleo solo necesita "enviar". Cómo se envía
    (push, email, SMS...) es asunto de los adaptadores.
    """

    @abstractmethod
    def send(self, notification: Notification) -> None: ...
