"""ERP client. To be implemented (see docs/*/02-requirements RF-05)."""

from __future__ import annotations

from meseta_ingesta.domain.models import Order


class ErpClient:
    def __init__(self, base_url: str, api_key: str, timeout_seconds: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key
        self.timeout_seconds = timeout_seconds

    def create_order(self, order: Order) -> str:
        """Create the order in the ERP and return the ERP order id."""
        raise NotImplementedError("ERP client is not implemented yet")
