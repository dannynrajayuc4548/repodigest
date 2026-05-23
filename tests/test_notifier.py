"""Tests for repodigest.notifier."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from repodigest.notifier import (
    NotificationError,
    NotifierConfig,
    notify,
    send_email,
    send_slack,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _email_config(**kwargs) -> NotifierConfig:
    base = dict(
        email_to="to@example.com",
        email_from="from@example.com",
        smtp_host="smtp.example.com",
        smtp_port=587,
        channels=["email"],
    )
    base.update(kwargs)
    return NotifierConfig(**base)


def _slack_config(**kwargs) -> NotifierConfig:
    base = dict(slack_webhook_url="https://hooks.slack.com/test", channels=["slack"])
    base.update(kwargs)
    return NotifierConfig(**base)


# ---------------------------------------------------------------------------
# send_email
# ---------------------------------------------------------------------------

def test_send_email_raises_without_addresses():
    cfg = NotifierConfig()
    with pytest.raises(NotificationError, match="email_to"):
        send_email(cfg, "Subject", "Body")


def test_send_email_calls_smtp(mocker):
    mock_smtp = MagicMock()
    mocker.patch("smtplib.SMTP", return_value=mock_smtp.__enter__.return_value)
    mock_smtp.__enter__.return_value = mock_smtp
    mock_smtp.__exit__.return_value = False

    cfg = _email_config(smtp_user="user", smtp_password="pass")
    with patch("smtplib.SMTP") as smtp_cls:
        instance = smtp_cls.return_value.__enter__.return_value
        send_email(cfg, "Weekly Digest", "Here is your digest.")
        smtp_cls.assert_called_once_with("smtp.example.com", 587)
        instance.login.assert_called_once_with("user", "pass")
        instance.send_message.assert_called_once()


# ---------------------------------------------------------------------------
# send_slack
# ---------------------------------------------------------------------------

def test_send_slack_raises_without_url():
    cfg = NotifierConfig()
    with pytest.raises(NotificationError, match="slack_webhook_url"):
        send_slack(cfg, "hello")


def test_send_slack_posts_json(mocker):
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.status = 200

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        send_slack(_slack_config(), "digest text")
        mock_open.assert_called_once()
        req = mock_open.call_args[0][0]
        body = json.loads(req.data)
        assert body["text"] == "digest text"


def test_send_slack_raises_on_bad_status(mocker):
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.status = 400

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with pytest.raises(NotificationError, match="HTTP 400"):
            send_slack(_slack_config(), "bad")


# ---------------------------------------------------------------------------
# notify dispatcher
# ---------------------------------------------------------------------------

def test_notify_unknown_channel_raises():
    cfg = NotifierConfig(channels=["carrier_pigeon"])
    with pytest.raises(NotificationError, match="carrier_pigeon"):
        notify(cfg, "S", "B")


def test_notify_returns_sent_channels(mocker):
    mocker.patch("repodigest.notifier.send_email")
    mocker.patch("repodigest.notifier.send_slack")
    cfg = NotifierConfig(
        channels=["email", "slack"],
        email_to="a@b.com",
        email_from="c@d.com",
        slack_webhook_url="https://hooks.slack.com/x",
    )
    sent = notify(cfg, "Subject", "Body")
    assert sent == ["email", "slack"]
