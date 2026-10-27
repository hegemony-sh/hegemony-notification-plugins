<!--
SPDX-FileCopyrightText: 2025-2026 Rexonix s.r.o.
SPDX-FileContributor: Jakub Trávník <jakub.travnik@gmail.com>
SPDX-License-Identifier: AGPL-3.0-or-later
-->

# hegemony-notification-plugins

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/License-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![CI](https://github.com/hegemony-sh/hegemony-notification-plugins/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/hegemony-sh/hegemony-notification-plugins/actions/workflows/ci.yml)
[![REUSE status](https://api.reuse.software/badge/github.com/hegemony-sh/hegemony-notification-plugins)](https://api.reuse.software/info/github.com/hegemony-sh/hegemony-notification-plugins)
[![Latest release](https://img.shields.io/github/v/release/hegemony-sh/hegemony-notification-plugins?label=Release)](https://github.com/hegemony-sh/hegemony-notification-plugins/releases)
[![FOSSA license scan](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fhegemony-sh%2Fhegemony-notification-plugins.svg?type=shield&issueType=license)](https://app.fossa.com/projects/git%2Bgithub.com%2Fhegemony-sh%2Fhegemony-notification-plugins?ref=badge_shield&issueType=license)
[![FOSSA security scan](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fhegemony-sh%2Fhegemony-notification-plugins.svg?type=shield&issueType=security)](https://app.fossa.com/projects/git%2Bgithub.com%2Fhegemony-sh%2Fhegemony-notification-plugins?ref=badge_shield&issueType=security)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/hegemony-sh/hegemony-notification-plugins/badge)](https://scorecard.dev/viewer/?uri=github.com/hegemony-sh/hegemony-notification-plugins)

The notification SDK and plugin wheels for
[Hegemony](https://github.com/hegemony-sh/hegemony), a self-hosted,
[Temporal](https://temporal.io/)-based orchestration platform for long-running
infrastructure changes. Hegemony sends notifications (run and approval events,
and the `flow.notify` step) through **destination types**. This repository holds
the SDK those types are written against, the transports Hegemony ships with, and
two optional packs of friendly presets:

| Package | What it is | Installed |
|---------|------------|-----------|
| `hegemony-notification-sdk` | The plugin contract: registry protocol, injected platform services, ABI version. Depends only on `pydantic`. | With the platform |
| `hegemony-notification-core-transports` | The `email` (SMTP), `shoutrrr` and `outgoing_webhook` transports. | With the platform |
| `hegemony-notification-shoutrrr-presets` | Telegram, Discord, Slack and Pushover destinations over `shoutrrr`. | Opt-in |
| `hegemony-notification-webhook-presets` | Webex incoming webhook and Teams (Power Automate) destinations over `outgoing_webhook`. | Opt-in |

The packages are published as GitHub release assets (wheels and a `SHA256SUMS`
file), not on PyPI. See [Install From A Release](#install-from-a-release).

## How it relates to the platform

The platform ([`hegemony-sh/hegemony`](https://github.com/hegemony-sh/hegemony))
owns the notification feature: destinations, subscriptions, the worker-side
dispatch, secret resolution and template rendering. It does not contain any
transport code. Every destination type, the built-in ones included, is loaded
from a plugin through the `hegemony.notification_providers` entry-point group.

A plugin depends only on `hegemony-notification-sdk` and exposes a
`register(registry)` callable. The host injects a `NotificationServices` (secret
resolution, template rendering) into each transport, so plugins never import
Hegemony internals. See the [SDK README](packages/notification_sdk/README.md).

- The SDK and all plugin wheels are released together under one semver tag,
  `vX.Y.Z`, cut automatically when a releasable change merges to `main`. Every
  package carries that version, and plugin wheels depend on the exact SDK
  version from the same release.
- The platform pins the release tag it is built and tested against in its
  `.github/plugin-pins.json`, and its own release is refused when a pin is not a
  released tag.
- The version is `0.x`: the plugin contract (`SDK_ABI_VERSION`) can change in a
  minor release. Breaking changes are listed in the [changelog](CHANGELOG.md).

## Documentation

- The documentation site is [hegemony.sh](https://hegemony.sh).
- [Notifications](https://github.com/hegemony-sh/hegemony/blob/main/docs/features/notifications.md)
  in the platform documentation describes the destination types, their
  configuration, templates and troubleshooting.
- [Installed Plugins](https://github.com/hegemony-sh/hegemony/blob/main/docs/guides/plugins.md)
  describes the **Settings → Installed Plugins** page, which lists every package
  and destination type an instance has loaded.
- Per package: the [SDK](packages/notification_sdk/README.md),
  [core transports](plugins/notification_core_transports/README.md),
  [Shoutrrr presets](plugins/notification_shoutrrr_presets/README.md) and
  [webhook presets](plugins/notification_webhook_presets/README.md).

## What is auto-installed vs opt-in

- **Auto-installed** with the platform (already present in Hegemony API and worker
  images): `hegemony-notification-sdk` and `hegemony-notification-core-transports` (the
  built-in `email`, `shoutrrr`, and `outgoing_webhook` transports).
- **Opt-in**: the preset packs (`hegemony-notification-shoutrrr-presets`,
  `hegemony-notification-webhook-presets`). Install only the packs a deployment wants.

A preset registers a friendly destination type that rewrites its config onto a base
transport. Both the **API** (to list/validate the destination type) and the **worker** (to
dispatch it) must have the pack installed. Restart both after installing so each registry
reloads its entry points. Do not use `--system`; Hegemony runs from `/opt/venv`.

## Install From A Release

Released wheels are published with a `SHA256SUMS` file. Verify downloaded wheels before
installing them. The example installs both preset packs into the API and worker; remove any
wheel names a deployment should not enable. Set `VERSION` to the release your Hegemony
version pins in its `.github/plugin-pins.json` (see [Compatibility](#compatibility)); the
newest is on the [Releases page](https://github.com/hegemony-sh/hegemony-notification-plugins/releases).
The SDK and the core transports are already in the Hegemony images, which is why the
example installs with `--no-deps`.

```bash
VERSION=X.Y.Z   # a release tag without the leading v; see Compatibility
API_CONTAINER=<your API container name>
WORKER_CONTAINER=<your worker container name>

for CONTAINER in "${API_CONTAINER}" "${WORKER_CONTAINER}"; do
  docker exec -u root -it "${CONTAINER}" bash -lc "
set -euo pipefail
version=${VERSION}
base=https://github.com/hegemony-sh/hegemony-notification-plugins/releases/download/v\${version}
tmp=\$(mktemp -d)
cd \"\${tmp}\"
curl -fsSLO \"\${base}/SHA256SUMS\"
for wheel in \
  hegemony_notification_shoutrrr_presets-\${version}-py3-none-any.whl \
  hegemony_notification_webhook_presets-\${version}-py3-none-any.whl
do
  curl -fsSLO \"\${base}/\${wheel}\"
  grep \"  \${wheel}$\" SHA256SUMS | sha256sum -c -
done
uv pip install --python /opt/venv/bin/python --no-deps ./*.whl
rm -rf \"\${tmp}\"
"
  docker restart "${CONTAINER}"
done
```

Or build local wheels from this repository and copy them into the running dev containers:

```bash
cd ../hegemony-notification-plugins
task build

for CONTAINER in hegemony-dev-api-1 hegemony-dev-worker-1; do
  docker exec -u root "${CONTAINER}" mkdir -p /tmp/notification-wheels
  docker cp dist/. "${CONTAINER}:/tmp/notification-wheels/"
  docker exec -u root -it "${CONTAINER}" bash -lc '
  uv pip install --python /opt/venv/bin/python --no-deps \
    /tmp/notification-wheels/hegemony_notification_shoutrrr_presets-*.whl \
    /tmp/notification-wheels/hegemony_notification_webhook_presets-*.whl
  '
  docker restart "${CONTAINER}"
done
```

These Docker-command installs are runtime changes. Re-run them after recreating a container
or replacing the image.

## Compatibility

Each Hegemony release pins one release of this repository in its
`.github/plugin-pins.json` and is built and tested against exactly that
release. Install the release your platform pins; the newest one is on the
[Releases page](https://github.com/hegemony-sh/hegemony-notification-plugins/releases).

| Hegemony | hegemony-notification-plugins |
| --- | --- |
| 1.0.0 | 0.3.2 |

Hegemony versions before 1.0.0 were not released publicly.

## Develop A Notification Plugin

A notification plugin is a wheel that exposes `register(registry)` under the
`hegemony.notification_providers` entry-point group and depends only on
`hegemony-notification-sdk`. There are two shapes:

- A **preset** adds a friendly destination type over an existing transport. It
  contributes a config schema and a pure, synchronous `build_config` that rewrites the
  friendly fields into the base transport's config. Start from the
  [Shoutrrr presets](plugins/notification_shoutrrr_presets/README.md) and the
  [SDK README](packages/notification_sdk/README.md).
- A **native transport** has its own `send` coroutine, for channels that no existing
  transport can express. The example below is one.

```python
# my_plugin/__init__.py
import httpx

from hegemony_notification_sdk import NotificationPluginRegistry, NotificationSendContext


async def send(ctx: NotificationSendContext) -> None:
    services = ctx.services
    ref = services.validate_secret_ref(
        ctx.config.get("url_ref"), field_name="url_ref", required=True
    )
    url = await services.resolve_secret_ref(ref, source="notification.example_chat")
    if not url:
        raise ValueError(f"Could not resolve '{ref}' - ensure the referenced secret exists.")
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json={"text": f"{ctx.title}\n\n{ctx.body}"})
    if response.is_error:
        # Never put the resolved URL or token into an error message or a log line.
        raise RuntimeError(f"Example Chat answered HTTP {response.status_code}")


def register(registry: NotificationPluginRegistry) -> None:
    registry.register_destination_type(
        destination_type="example_chat",
        display_name="Example Chat",
        description="Post to an Example Chat incoming webhook.",
        send=send,
        config_schema={
            "type": "object",
            "required": ["url_ref"],
            "properties": {
                "url_ref": {
                    "type": "string",
                    "x_secret_ref": True,
                    "title": "Webhook URL (secret reference)",
                },
            },
        },
    )
```

```toml
# pyproject.toml
[project]
name = "my-notification-plugin"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["hegemony-notification-sdk>=0.3,<0.4", "httpx>=0.27"]

[project.entry-points."hegemony.notification_providers"]
my_plugin = "my_plugin:register"
```

The rules a plugin follows:

- Import nothing from Hegemony. Secret resolution and template rendering come from the
  injected `NotificationServices`; a destination field that holds a secret is a secret
  reference (`x_secret_ref` in its schema), validated with `validate_secret_ref` and
  resolved with `resolve_secret_ref` at send time.
- Do not write a resolved secret, token or webhook URL to a log or an error message.
- `build_config` of a preset is pure and synchronous: no I/O, no secret resolution.
- Raise on failure. The host catches the exception, counts the destination as failed and
  logs the exception's message, which is one more reason to keep secrets out of it.
- Test against an in-memory `NotificationServices`, as
  [`tests/test_core_transports.py`](tests/test_core_transports.py) does with its
  `FakeServices`. Use example hosts (`example.com`) and synthetic credentials in tests,
  never a real endpoint.

The SDK is not on PyPI. To develop against it, install a release wheel, or install it from
this repository at a release tag (replace `X.Y.Z` with the release your platform pins):

```bash
uv pip install "git+https://github.com/hegemony-sh/hegemony-notification-plugins@vX.Y.Z#subdirectory=packages/notification_sdk"
```

Install your wheel into both the API and the worker, as in
[Install From A Release](#install-from-a-release), and restart both. The new destination
type then appears under **Settings → Installed Plugins** and in the destination form of
the **Notifications** screen. `SDK_ABI_VERSION` is the registration contract's version;
the platform exposes its value as `registry.api_version`, so a plugin can check it.

## Development

```bash
uv sync --all-packages
uv run pre-commit install --install-hooks
```

If you have [Task](https://taskfile.dev/) installed, the common workflow is:

```bash
task setup
task lint
task test
task build
task smoke
```

The hook set mirrors Hegemony where applicable for this package-only repo: general file
hygiene, pyproject validation, typos, Zizmor, workflow schema checks, REUSE, Ruff,
typecheck, tests, Gitleaks, and commitlint. UI, Docker, OpenAPI, and task-runner hooks stay
in Hegemony because those surfaces are not present here.

Run the local equivalent of CI:

```bash
task ci
```

Run every configured pre-commit hook manually:

```bash
task precommit
```

Releases are cut automatically when a releasable change merges to `main`; see
[Contributing](CONTRIBUTING.md#releasing). Do not bump versions or push tags by
hand. `task version:set -- X.Y.Z` and `task version:verify -- vX.Y.Z` stay
available for trying the lockstep bump locally.

## Contributing, security and licence

- Read [Contributing](CONTRIBUTING.md) first. Every commit needs a DCO sign-off
  (`git commit -s`) and follows Conventional Commits, because merges to `main`
  drive releases: `feat`, `fix`, `perf` and `revert` commits publish a new
  version.
- Report vulnerabilities privately, as [SECURITY.md](SECURITY.md) describes, and
  do not open public issues for them.
- Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
- Licensed under `AGPL-3.0-or-later`. See [Licensing](LICENSING.md).

[![FOSSA license report](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fhegemony-sh%2Fhegemony-notification-plugins.svg?type=large&issueType=license)](https://app.fossa.com/projects/git%2Bgithub.com%2Fhegemony-sh%2Fhegemony-notification-plugins?ref=badge_large&issueType=license)
