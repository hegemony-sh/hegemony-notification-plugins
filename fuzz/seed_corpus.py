# SPDX-FileCopyrightText: 2026 Rexonix s.r.o.
# SPDX-FileContributor: Jakub Trávník <jakub.travnik@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Generate deterministic raw UTF-8 seed inputs; no external data or credentials."""

import hashlib
import sys
from pathlib import Path

SOURCES = {
    "webhook_url_fuzzer": "hegemony_notification_core_transports.outgoing_webhook",
    "webhook_signing_fuzzer": "hegemony_notification_core_transports.outgoing_webhook",
}

SEEDS = {
    "webhook_url_fuzzer": [
        "https://webhook.example/path?token=synthetic-query",
        "https://synthetic-user:synthetic-password@/private-path",
        "https://[::1]/path",
        "https://host.example:99999/path",
        "file:///tmp/example",
        "https://[invalid/",
        "https://webhook.example/path\r\n",
    ],
    "webhook_signing_fuzzer": [
        "",
        "body",
        '{"title":"synthetic","body":"line\\nquote\\""}',
        "\x00unicode: žluťoučký",
        "ÿtimestamped",
    ],
}


def seed_corpus(root: Path) -> None:
    for name, seeds in SEEDS.items():
        directory = root / name
        directory.mkdir(parents=True, exist_ok=True)
        for seed in seeds:
            data = seed.encode("utf-8")
            (directory / hashlib.sha256(data).hexdigest()).write_bytes(data)


if __name__ == "__main__":
    seed_corpus(Path(sys.argv[1]))
