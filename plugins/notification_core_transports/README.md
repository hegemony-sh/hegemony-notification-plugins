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
