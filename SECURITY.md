<!--
SPDX-FileCopyrightText: 2025-2026 Rexonix s.r.o.
SPDX-FileContributor: Jakub Trávník <jakub.travnik@gmail.com>

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Security Policy

Security reports are handled privately. Please do not open a public GitHub issue for vulnerabilities, suspected vulnerabilities, leaked secrets, or exploit details.

This repository holds the notification SDK and plugin wheels of [Hegemony](https://github.com/hegemony-sh/hegemony). Vulnerabilities in the platform itself are reported the same way, to the same address; see the platform's [Security Policy](https://github.com/hegemony-sh/hegemony/blob/develop/SECURITY.md).

## Supported versions

Every package in this repository is released together under one version, `vX.Y.Z`, from the `main` branch. There are no maintenance branches: a security fix is merged to `main` and published as a new release, which is a patch release for a fix. Releases are immutable and are never changed after they are published, so run the newest release.

The platform pins the exact release it is built against, and its [Security Policy](https://github.com/hegemony-sh/hegemony/blob/develop/SECURITY.md#supported-versions) sets which Hegemony versions receive security fixes.

## Reporting a vulnerability

Report vulnerabilities privately by emailing [security@hegemony.sh](mailto:security@hegemony.sh).

Please include as much detail as you can safely share:

- Affected package (`hegemony-notification-sdk`, `hegemony-notification-core-transports`, `hegemony-notification-shoutrrr-presets` or `hegemony-notification-webhook-presets`) and, when it applies, the destination type (`email`, `shoutrrr`, `outgoing_webhook`, or a preset).
- Impact and attack scenario.
- Reproduction steps or proof-of-concept details.
- Affected versions and commits, and the Hegemony version they run in.
- Whether the issue is already public or under active exploitation.
- A safe way to contact you for follow-up.

Reports about the handling of secrets are in scope. A transport that writes a resolved secret, token, or webhook URL to a log or an error message, or that accepts a raw credential where a secret reference is required, is a vulnerability.

Do not include real credentials, SMTP passwords, webhook URLs, or bot tokens in a report. Use placeholders and example hosts.

## Response targets

Maintainers aim to follow this timeline:

| Stage | Target |
| --- | --- |
| Acknowledge receipt | 48 hours |
| Initial triage and severity assessment | 7 days |
| Coordinated fix and disclosure target | 90 days |

These targets may vary based on severity, complexity, affected dependencies, maintainer availability, and responsible-disclosure coordination.

## Disclosure process

1. Maintainers acknowledge the report and establish a private coordination channel.
2. Maintainers validate the report, assess severity, and identify affected versions.
3. A fix, mitigation, or advisory is prepared privately.
4. Disclosure timing is coordinated with the reporter when possible.
5. Public details are published after a fix or mitigation is available, or after the coordinated disclosure window expires. The fix ships as a release of this repository, and its release notes link the advisory when there is one.

## Safe harbor

Security research conducted in good faith is welcome. Please avoid privacy violations, service disruption, data destruction, persistence, social engineering, spam, and testing against systems you do not own or do not have permission to test.

## Secrets

If you believe a secret was committed or exposed, report it privately. Do not rotate, use, or test credentials unless they belong to you and you are authorized to do so.
