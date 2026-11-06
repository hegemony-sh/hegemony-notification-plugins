#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Rexonix s.r.o.
# SPDX-FileContributor: Jakub Trávník <jakub.travnik@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Exercise URL validation and ensure diagnostic summaries strip synthetic credentials."""

import sys
from urllib.parse import quote, urlparse

import atheris

with atheris.instrument_imports(include=["hegemony_notification_core_transports"]):
    from hegemony_notification_core_transports.outgoing_webhook import (
        _redact_url,
        _validate_resolved_webhook_url,
    )


@atheris.instrument_func
def test_one_input(data: bytes) -> None:
    raw = data[:16384].decode("utf-8", errors="replace")
    assert isinstance(_redact_url(raw), str)
    try:
        normalized = _validate_resolved_webhook_url(raw)
    except ValueError:
        pass
    else:
        parsed = urlparse(normalized)
        assert parsed.scheme in ("http", "https") and parsed.netloc
        assert parsed.username is None and parsed.password is None
        assert normalized == raw.strip()
    fdp = atheris.FuzzedDataProvider(data)
    host = "node" + str(fdp.ConsumeIntInRange(0, 999)) + ".example"
    path = "/private-path/" + quote(raw[:128], safe="")
    url = "https://" + host + path + "?token=synthetic-query#synthetic-fragment"
    assert _validate_resolved_webhook_url("  " + url + "  ") == url
    assert _redact_url(url) == "https://" + host + "/…"
    for destination in (host, ""):
        credential_url = (
            "https://synthetic-user:synthetic-password@"
            + destination
            + path
            + "?token=synthetic-query"
        )
        summary = _redact_url(credential_url)
        for sensitive in (
            "synthetic-user",
            "synthetic-password",
            "private-path",
            "synthetic-query",
        ):
            assert sensitive not in summary, summary
        try:
            _validate_resolved_webhook_url(credential_url)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted embedded credentials")


if __name__ == "__main__":
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()
