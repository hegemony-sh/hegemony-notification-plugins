<!--
SPDX-FileCopyrightText: 2025-2026 Rexonix s.r.o.
SPDX-FileContributor: Jakub Trávník <jakub.travnik@gmail.com>

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# hegemony-notification-core-transports

The notification transports Hegemony ships with, packaged as a plugin:

| Destination | Notes |
|-------------|-------|
| `email` | SMTP via `aiosmtplib`; every setting comes from the destination config |
| `shoutrrr` | Raw Shoutrrr service URL (needs the `shoutrrr` binary) |
| `outgoing_webhook` | HTTP webhook with auth, TLS, HMAC signing, retries (`httpx`) |

Unlike third-party notification plugins, this one is **auto-installed** with the platform
(it's a path dependency of the host, like `hegemony-notification-sdk`) so notifications
work out of the box. Secret resolution and template rendering are provided by the host via
the injected `NotificationServices`; this package never imports platform internals.

## Configuration reference

These are the runtime configuration keys accepted by each transport. Some
advanced keys are not listed in the compact registration schema. Preset
`build_config` functions return these dictionaries and preserve protected
secret references; the host resolves them when sending.

### Email

| Key | Meaning and default |
| --- | --- |
| `to` | Required recipient list; at least one resolved address |
| `cc` | Optional recipient list; empty by default |
| `from` | Required sender address |
| `smtp_host_ref` | Required protected reference for the SMTP hostname |
| `smtp_port_ref` | Optional protected reference; resolved integer port, default `587` |
| `smtp_username_ref` / `smtp_password_ref` | Optional protected references for SMTP authentication |
| `smtp_use_tls_ref` | Optional protected reference; resolves to `true` to use implicit TLS; default `false` |
| `smtp_use_starttls_ref` | Optional protected reference; resolves to `true` to use STARTTLS; default `true` |

Address fields pass through host reference validation and resolution too.
The host-supplied title becomes the subject and the body becomes plain-text
content. Sending has a 60-second timeout. Set TLS and STARTTLS appropriately
for the server; do not enable both simultaneously.

### Shoutrrr

| Key | Meaning |
| --- | --- |
| `url_secret` | Required protected reference resolving to a complete Shoutrrr service URL |

The transport runs the installed `shoutrrr` executable with the resolved URL
and the title/body message. The CLI timeout is 30 seconds; nonzero exit status
or timeout fails delivery. There is no configurable timeout key.

### Outgoing webhook

| Key | Meaning and default |
| --- | --- |
| `url` | Required HTTP(S) URL; supports host-rendered templates; embedded username/password is rejected |
| `method` | Request method; schema offers `POST` and `PUT`; default `POST` |
| `headers` | Optional header dictionary, layered over `Content-Type: application/json` |
| `payload_template` | Optional message template rendered with title/body; otherwise JSON containing `title` and `body` |
| `timeout_seconds` | HTTP timeout; default `30` |
| `retry_count` | Retries after the initial attempt; default `3` |
| `retry_backoff_seconds` | Initial exponential backoff; default `2` seconds |
| `verify_tls` | Certificate verification; default `true`; disabling it removes certificate authentication |
| `custom_ca_bundle` | Optional PEM CA certificates added to a default SSL context |
| `auth_type` | `none` (default), `bearer`, `basic`, or `custom_header` |
| `auth_token_ref` | Required protected token reference for bearer authentication |
| `auth_username` / `auth_password_ref` | Basic-auth username (default empty) and required protected password reference |
| `auth_header_name` / `auth_header_value_ref` | Valid nonempty header name and required protected value reference for custom-header authentication |
| `signing` | Optional signing-policy object, described below; omitted means no signing |

Authentication headers override matching entries from `headers`. A signing
policy then adds its headers. Successful HTTP responses finish delivery;
HTTP 4xx responses other than 429 are not retried. Use HTTPS for credentials
and sensitive message content.

The `signing` object accepts:

| Key | Meaning and default |
| --- | --- |
| `algorithm` | Only `hmac-sha256` is supported; it is the default |
| `secret_ref` | Required protected reference resolving to a nonempty signing key |
| `signature_header` | Header containing the hexadecimal HMAC; default `X-Webhook-Signature` |
| `timestamp_header` | Optional header for the Unix timestamp in seconds |
| `signed_content` | `body` (default) or `timestamp_dot_body`; the latter requires `timestamp_header` |
| `prefix` | String prepended to the hexadecimal signature; default empty |

The signature covers the actual payload bytes, or the timestamp followed by
a dot and those bytes. Supply a strong randomly generated signing key through
the host secret store. Do not put resolved credentials in preset output or logs.
