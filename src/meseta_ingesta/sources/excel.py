"""Excel (.xlsx) source. To be implemented (see docs/*/02-requirements RF-01)."""

from __future__ import annotations

from pathlib import Path

from meseta_ingesta.domain.models import Order


def parse_workbook(path: Path) -> list[Order]:
    raise NotImplementedError("Excel parsing is not implemented yet")
