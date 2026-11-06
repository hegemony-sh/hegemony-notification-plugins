#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Rexonix s.r.o.
# SPDX-FileContributor: Jakub Trávník <jakub.travnik@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Verify signature contents and header preservation using an offline secret service."""

import asyncio
import hashlib
import sys
from unittest.mock import patch

import atheris

with atheris.instrument_imports(include=["hegemony_notification_core_transports"]):
    from hegemony_notification_core_transports.outgoing_webhook import _apply_signing_policy


class Services:
    def validate_secret_ref(self, ref, **kwargs):
        assert ref == "synthetic-ref"
        return ref

    async def resolve_secret_ref(self, ref, **kwargs):
        assert ref == "synthetic-ref"
        return "synthetic-signing-value"


@atheris.instrument_func
def test_one_input(data: bytes) -> None:
    """Compare signatures with an independent oracle and reject invalid policies."""
    fdp = atheris.FuzzedDataProvider(data)
    timestamped = fdp.ConsumeBool()
    prefix = fdp.ConsumeUnicodeNoSurrogates(32)
    payload = data[:16384]
    policy = {
        "secret_ref": "synthetic-ref",
        "signature_header": "X-Signature",
        "prefix": prefix,
        "signed_content": "timestamp_dot_body" if timestamped else "body",
    }
    if timestamped:
        policy["timestamp_header"] = "X-Time"
    headers = {"Content-Type": "application/json", "X-Unrelated": "preserved"}
    with patch(
        "hegemony_notification_core_transports.outgoing_webhook.time.time", return_value=1700000000
    ):
        asyncio.run(_apply_signing_policy(Services(), policy, payload, headers))
    message = b"1700000000." + payload if timestamped else payload
    # Independent RFC 2104 construction instead of calling the implementation's
    # hmac.new helper. The synthetic key fits in SHA-256's 64-byte block.
    key = b"synthetic-signing-value".ljust(64, b"\0")
    inner = hashlib.sha256(bytes(b ^ 0x36 for b in key) + message).digest()
    signature = hashlib.sha256(bytes(b ^ 0x5C for b in key) + inner).hexdigest()
    expected = {
        "Content-Type": "application/json",
        "X-Unrelated": "preserved",
        "X-Signature": prefix + signature,
    }
    if timestamped:
        expected["X-Time"] = "1700000000"
    assert headers == expected
    for invalid in ({"algorithm": "unsupported"}, {"signed_content": "timestamp_dot_body"}):
        bad_policy = {"secret_ref": "synthetic-ref", **invalid}
        untouched = {"X-Unrelated": "preserved"}
        try:
            asyncio.run(_apply_signing_policy(Services(), bad_policy, payload, untouched))
        except ValueError:
            assert untouched == {"X-Unrelated": "preserved"}
        else:
            raise AssertionError("accepted an invalid signing policy")


if __name__ == "__main__":
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()
