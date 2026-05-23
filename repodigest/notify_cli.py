"""CLI helpers that wire NotifierConfig into the main repodigest workflow."""
from __future__ import annotations

import argparse
from typing import Optional

from repodigest.notifier import NotifierConfig, notify, NotificationError


def add_notify_args(parser: argparse.ArgumentParser) -> None:
    """Attach notification-related arguments to *parser*."""
    grp = parser.add_argument_group("notifications")
    grp.add_argument(
        "--notify",
        metavar="CHANNEL",
        action="append",
        dest="notify_channels",
        choices=["email", "slack"],
        help="Notification channel to use (may be repeated). Choices: email, slack.",
    )
    grp.add_argument("--email-to", metavar="ADDR", help="Recipient e-mail address.")
    grp.add_argument("--email-from", metavar="ADDR", help="Sender e-mail address.")
    grp.add_argument("--smtp-host", default="localhost", metavar="HOST")
    grp.add_argument("--smtp-port", type=int, default=25, metavar="PORT")
    grp.add_argument("--smtp-user", metavar="USER")
    grp.add_argument("--smtp-password", metavar="PASS")
    grp.add_argument("--slack-webhook-url", metavar="URL")


def build_notifier_config(args: argparse.Namespace) -> Optional[NotifierConfig]:
    """Construct a :class:`NotifierConfig` from parsed *args*, or ``None``."""
    channels = args.notify_channels or []
    if not channels:
        return None
    return NotifierConfig(
        channels=channels,
        email_to=args.email_to,
        email_from=args.email_from,
        smtp_host=args.smtp_host,
        smtp_port=args.smtp_port,
        smtp_user=args.smtp_user,
        smtp_password=args.smtp_password,
        slack_webhook_url=args.slack_webhook_url,
    )


def dispatch_notifications(
    notifier_config: Optional[NotifierConfig],
    subject: str,
    body: str,
    *,
    verbose: bool = False,
) -> None:
    """Send notifications if *notifier_config* is provided.

    Prints a confirmation line for each channel when *verbose* is True.
    Errors are re-raised as :class:`~repodigest.notifier.NotificationError`.
    """
    if notifier_config is None:
        return
    sent = notify(notifier_config, subject, body)
    if verbose:
        for channel in sent:
            print(f"[notify] Digest sent via {channel}.")
