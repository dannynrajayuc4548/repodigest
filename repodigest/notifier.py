"""Notification support: send digest summaries via configurable channels."""
from __future__ import annotations

import smtplib
import urllib.request
import urllib.parse
import json
from email.message import EmailMessage
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NotifierConfig:
    """Holds notification channel configuration."""
    email_to: Optional[str] = None
    email_from: Optional[str] = None
    smtp_host: str = "localhost"
    smtp_port: int = 25
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    channels: list[str] = field(default_factory=list)


class NotificationError(Exception):
    """Raised when a notification fails to send."""


def send_email(config: NotifierConfig, subject: str, body: str) -> None:
    """Send *body* via SMTP using *config*."""
    if not config.email_to or not config.email_from:
        raise NotificationError("email_to and email_from must be set for email notifications")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.email_from
    msg["To"] = config.email_to
    msg.set_content(body)

    try:
        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            if config.smtp_user and config.smtp_password:
                server.login(config.smtp_user, config.smtp_password)
            server.send_message(msg)
    except smtplib.SMTPException as exc:
        raise NotificationError(f"SMTP error: {exc}") from exc


def send_slack(config: NotifierConfig, text: str) -> None:
    """Post *text* to a Slack incoming webhook."""
    if not config.slack_webhook_url:
        raise NotificationError("slack_webhook_url must be set for Slack notifications")

    payload = json.dumps({"text": text}).encode()
    req = urllib.request.Request(
        config.slack_webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status not in (200, 204):
                raise NotificationError(f"Slack returned HTTP {resp.status}")
    except OSError as exc:
        raise NotificationError(f"Slack request failed: {exc}") from exc


def notify(config: NotifierConfig, subject: str, body: str) -> list[str]:
    """Dispatch notifications for every channel listed in *config.channels*.

    Returns a list of channel names that succeeded.
    """
    sent: list[str] = []
    for channel in config.channels:
        if channel == "email":
            send_email(config, subject, body)
            sent.append("email")
        elif channel == "slack":
            send_slack(config, body)
            sent.append("slack")
        else:
            raise NotificationError(f"Unknown notification channel: {channel!r}")
    return sent
