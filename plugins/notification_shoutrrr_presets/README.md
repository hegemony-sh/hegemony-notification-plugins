<!--
SPDX-FileCopyrightText: 2025-2026 Rexonix s.r.o.
SPDX-FileContributor: Jakub Trávník <jakub.travnik@gmail.com>

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# hegemony-notification-shoutrrr-presets

Friendly notification presets built on Hegemony's `shoutrrr` transport. Instead
of asking users to hand-craft a Shoutrrr service URL, each preset exposes a few
simple fields and assembles the URL for them:

| Destination | Fields |
|-------------|--------|
| `telegram`  | bot token (secret), chat IDs |
| `discord`   | webhook token (secret), webhook ID |
| `slack`     | webhook tokens (secret), bot name (optional) |
| `pushover`  | API token (secret), user key, devices (optional) |

Token fields are entered as secret references (e.g.
`{{ secret('vault://telegram/token') }}`) and are passed through to the host's
Shoutrrr transport, which resolves them at send time — this plugin never handles
secret values.

## Install

The wheel is a release asset of this repository, not a PyPI package. Install it
into both the API and the worker as described in
[Install From A Release](../../README.md#install-from-a-release), then restart
both.

The host discovers it automatically via the
`hegemony.notification_providers` entry-point group. Requires the host's
built-in `shoutrrr` transport and the `shoutrrr` binary.
