<!--
SPDX-FileCopyrightText: 2025-2026 Rexonix s.r.o.
SPDX-FileContributor: Jakub Trávník <jakub.travnik@gmail.com>

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# hegemony-notification-sdk

Public, dependency-light SDK for building **Hegemony notification plugins** —
out-of-tree wheels that add notification destination types to the core platform
at runtime.

A plugin depends only on this package (which depends only on `pydantic`) and
exposes a `register(registry)` callable under the
`hegemony.notification_providers` entry-point group:

```toml
# In your plugin's pyproject.toml
[project]
dependencies = ["hegemony-notification-sdk>=0.3,<0.4"]

[project.entry-points."hegemony.notification_providers"]
my_plugin = "my_plugin:register"
```

The SDK is released together with the plugins in this repository, as a wheel
attached to each GitHub release; it is not published on PyPI. While the major
version is 0, an incompatible change to the contract is released as a new minor
version, so depend on one minor line. The repository
[README](../../README.md#develop-a-notification-plugin) walks through a complete
transport and how to install a plugin into a Hegemony instance.

## Presets (recommended)

The simplest way to add a user-friendly channel is a **preset** over an existing
transport. The plugin contributes a friendly `config_schema` and a *pure*
`build_config` that rewrites the friendly fields into the base transport's
config. Secret references pass through untouched — the host's base transport
resolves them at send time, so the plugin never handles secrets or performs I/O.

```python
# my_plugin/__init__.py
from hegemony_notification_sdk import NotificationPluginRegistry


def register(registry: NotificationPluginRegistry) -> None:
    registry.register_preset(
        destination_type="telegram",
        display_name="Telegram",
        description="Send via a Telegram bot.",
        base_transport="shoutrrr",
        build_config=lambda cfg: {
            "url_secret": f"telegram://{cfg['token']}@telegram?chats={cfg['chats']}"
        },
        config_schema={
            "type": "object",
            "required": ["token", "chats"],
            "properties": {
                "token": {"type": "string", "title": "Bot token (secret reference)"},
                "chats": {"type": "string", "title": "Chat IDs (comma-separated)"},
            },
        },
    )
```

## Native transports

For channels that cannot be expressed as a preset, register a native
destination type with its own `send` coroutine via
`register_destination_type(...)`.

## ABI

`SDK_ABI_VERSION` is bumped only on incompatible changes to the registration
contract. The platform exposes its value as `registry.api_version` so a plugin
can self-gate if needed.

## API reference

Import public contracts from `hegemony_notification_sdk`. This SDK exposes
Python interfaces, not an HTTP endpoint.

| Interface | Inputs | Result and calling convention |
| --- | --- | --- |
| `register_destination_type` | Keyword-only destination type, display name, description, `send`, and optional configuration schema | Synchronous registration; returns `None` |
| `register_preset` | The same identity fields, base transport, pure `build_config`, and optional configuration schema | Synchronous registration; returns `None` |
| `BuildConfigFn` | Configuration dictionary | Synchronously returns the base transport's configuration dictionary; no I/O or secret resolution |
| `SendFn` | `NotificationSendContext` | Await the send coroutine; returns `None` on success and raises on failure |

`NotificationSendContext` carries the configuration dictionary, message title,
message body and injected `NotificationServices`. The host formats the title
and body before dispatch. A transport uses these services:

| Service | Inputs | Result and calling convention |
| --- | --- | --- |
| `resolve_secret_ref` | Reference or `None`; keyword-only `source` | Async; await for a secret string or `None` |
| `validate_secret_ref` | Reference; keyword-only field name and optional required flag | Synchronous; normalized reference or `None`; raises on invalid input |
| `render_message` | Template; keyword-only title, body and optional JSON-escaping flag | Synchronous; rendered string |
| `render_template` | Full-scope template string | Async; await for the resolved string |
| `contains_template` | String | Synchronous; boolean |

For example, use
`await ctx.services.resolve_secret_ref(ref, source="notification.my_plugin")`.
Keep resolved secrets out of logs and error messages. Presets pass protected
references through unchanged.

From the repository root, render complete signatures and docstrings with:

```bash
uv sync --frozen --all-packages
uv run python -m pydoc hegemony_notification_sdk
uv run python -m pydoc hegemony_notification_sdk.registry
uv run python -m pydoc hegemony_notification_sdk.services
```

For local HTML browsing, run `uv run python -m pydoc -b`, open the SDK module,
and follow its class/module links; stop the server when finished. With an
installed SDK, omit `uv run`. Transport configuration and preset fields are
documented in the [core transports](../../plugins/notification_core_transports/README.md),
[Shoutrrr presets](../../plugins/notification_shoutrrr_presets/README.md), and
[webhook presets](../../plugins/notification_webhook_presets/README.md) references.
