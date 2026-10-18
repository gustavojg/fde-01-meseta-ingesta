"""Email (IMAP) source. To be implemented (see docs/*/02-requirements RF-02)."""

from __future__ import annotations

from meseta_ingesta.domain.models import Order


def parse_message(raw_message: bytes) -> list[Order]:
    raise NotImplementedError("Email parsing is not implemented yet")
