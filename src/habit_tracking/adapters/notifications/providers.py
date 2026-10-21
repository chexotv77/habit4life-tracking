"""
Mocks de proveedores externos de mensajería.

Cada uno tiene su PROPIA firma, incompatible con NotificationPort (es justo lo
que motiva el patrón Adapter). En producción serían SDKs reales (Firebase,
un servidor SMTP, una pasarela SMS); aquí solo guardan lo enviado para poder
inspeccionarlo en las pruebas.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FcmClient:
    """Proveedor de push estilo Firebase: dispatch(device_token, payload)."""

    sent: list[dict] = field(default_factory=list)

    def dispatch(self, device_token: str, payload: dict) -> None:
        self.sent.append({"token": device_token, "payload": payload})


@dataclass
class SmtpServer:
    """Servidor de correo: send_mail(to_addr, subject, html_body)."""

    outbox: list[dict] = field(default_factory=list)

    def send_mail(self, to_addr: str, subject: str, html_body: str) -> None:
        self.outbox.append({"to": to_addr, "subject": subject, "html": html_body})


@dataclass
class SmsGateway:
    """Pasarela SMS: send_text(phone_number, text)."""

    log: list[dict] = field(default_factory=list)

    def send_text(self, phone_number: str, text: str) -> None:
        self.log.append({"number": phone_number, "text": text})
