# SPDX-FileCopyrightText: 2025-2026 Rexonix s.r.o.
# SPDX-FileContributor: Jakub Trávník <jakub.travnik@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Email transport using aiosmtplib.

Every SMTP setting comes from the destination config (``smtp_*_ref``, ``from``). An empty
port, TLS or STARTTLS field takes a fixed default (587, off, on); the sender and host have
none and must be set. Secret references (``{{ secret() }}``) are resolved by the injected
services, never by this plugin directly.
"""

import logging
from email.message import EmailMessage
from typing import Any

from hegemony_notification_sdk import NotificationSendContext, NotificationServices

logger = logging.getLogger(__name__)

# Used as-is when the field is left empty; never passed to the host's template engine.
DEFAULT_SMTP_PORT = "587"
DEFAULT_SMTP_USE_TLS = "false"
DEFAULT_SMTP_USE_STARTTLS = "true"


async def _resolve_config_value(
    services: NotificationServices,
    ref: str | None,
    *,
    field_name: str,
    required: bool = False,
    default: str | None = None,
) -> str | None:
    """Resolve a config value (template ref or literal), or return ``default`` when empty."""
    ref = services.validate_secret_ref(ref, field_name=field_name, required=required)
    if ref is None:
        return default
    value = await services.resolve_secret_ref(ref, source=f"notification.email.{field_name}")
    if value is None:
        raise ValueError(f"'{ref}' could not be resolved for '{field_name}'")
    return value


async def _resolve_addresses(
    services: NotificationServices, addresses: list[Any], *, field_name: str
) -> list[str]:
    """Resolve each recipient address (literals pass through; empties dropped)."""
    resolved: list[str] = []
    for addr in addresses:
        if not isinstance(addr, str) or not addr.strip():
            continue
        value = await _resolve_config_value(services, addr, field_name=field_name)
        if value and value.strip():
            resolved.append(value.strip())
    return resolved


async def _get_smtp_config(
    services: NotificationServices, config: dict[str, Any]
) -> dict[str, Any]:
    """Resolve the SMTP connection settings from the destination config."""
    host = await _resolve_config_value(
        services, config.get("smtp_host_ref"), field_name="smtp_host_ref", required=True
    )
    port_value = await _resolve_config_value(
        services,
        config.get("smtp_port_ref"),
        field_name="smtp_port_ref",
        default=DEFAULT_SMTP_PORT,
    )
    use_tls_value = await _resolve_config_value(
        services,
        config.get("smtp_use_tls_ref"),
        field_name="smtp_use_tls_ref",
        default=DEFAULT_SMTP_USE_TLS,
    )
    start_tls_value = await _resolve_config_value(
        services,
        config.get("smtp_use_starttls_ref"),
        field_name="smtp_use_starttls_ref",
        default=DEFAULT_SMTP_USE_STARTTLS,
    )
    return {
        "host": host,
        "port": int(port_value) if port_value is not None else 587,
        "username": await _resolve_config_value(
            services, config.get("smtp_username_ref"), field_name="smtp_username_ref"
        ),
        "password": await _resolve_config_value(
            services, config.get("smtp_password_ref"), field_name="smtp_password_ref"
        ),
        "use_tls": str(use_tls_value).lower() == "true",
        "start_tls": str(start_tls_value).lower() == "true",
    }


async def send(ctx: NotificationSendContext) -> None:
    """Send an email notification."""
    config, title, body, services = ctx.config, ctx.title, ctx.body, ctx.services
    try:
        import aiosmtplib
    except ImportError as err:
        raise ImportError(
            "aiosmtplib is required for email notifications. Install with: pip install aiosmtplib"
        ) from err

    smtp_config = await _get_smtp_config(services, config)
    msg = EmailMessage()

    to_addrs = config.get("to", [])
    if not isinstance(to_addrs, list):
        to_addrs = [to_addrs] if to_addrs else []
    to_addrs = await _resolve_addresses(services, to_addrs, field_name="to")
    if not to_addrs:
        raise ValueError("Email destination requires at least one 'to' address")
    msg["To"] = ", ".join(to_addrs)

    cc_addrs = config.get("cc", [])
    if not isinstance(cc_addrs, list):
        cc_addrs = [cc_addrs] if cc_addrs else []
    cc_addrs = await _resolve_addresses(services, cc_addrs, field_name="cc")
    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)

    from_addr = await _resolve_config_value(services, config.get("from"), field_name="from")
    if not from_addr or not from_addr.strip():
        raise ValueError("Email destination requires a sender address: set 'from' in its config")
    msg["From"] = from_addr

    # Title/body (incl. any per-destination override) are finalized by the host before
    # dispatch; the transport just renders them.
    msg["Subject"] = title
    msg.set_content(body)

    all_recipients = to_addrs + cc_addrs
    logger.debug(
        "Sending email to %d recipient(s) via %s:%s",
        len(all_recipients),
        smtp_config["host"],
        smtp_config["port"],
    )
    await aiosmtplib.send(
        msg,
        hostname=smtp_config["host"],
        port=smtp_config["port"],
        username=smtp_config["username"],
        password=smtp_config["password"],
        use_tls=smtp_config["use_tls"],
        start_tls=smtp_config["start_tls"],
        timeout=60,
    )
    logger.info("Email sent successfully to %d recipient(s)", len(all_recipients))


CONFIG_SCHEMA = {
    "type": "object",
    "required": ["to", "from", "smtp_host_ref"],
    "properties": {
        "to": {"type": "array", "items": {"type": "string"}, "title": "To"},
        "cc": {"type": "array", "items": {"type": "string"}, "title": "Cc"},
        "from": {"type": "string", "title": "From"},
        "smtp_host_ref": {"type": "string", "x_secret_ref": True, "title": "SMTP host"},
        "smtp_port_ref": {"type": "string", "x_secret_ref": True, "title": "SMTP port"},
        "smtp_username_ref": {"type": "string", "x_secret_ref": True, "title": "SMTP username"},
        "smtp_password_ref": {"type": "string", "x_secret_ref": True, "title": "SMTP password"},
    },
}
