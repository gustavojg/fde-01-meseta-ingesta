"""Canonical order model.

Every source (Excel, email) is parsed into `Order`. The ERP client only ever
receives `Order` instances, never raw rows or email bodies.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class Source(StrEnum):
    EXCEL = "excel"
    EMAIL = "email"


class OrderLine(BaseModel):
    description: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    weight_kg: float | None = Field(default=None, ge=0)
    volume_m3: float | None = Field(default=None, ge=0)


class Order(BaseModel):
    """A transport order as understood by the business.

    `external_ref` is the customer's own reference and, together with
    `customer_code`, is the key used to detect duplicates.
    """

    customer_code: str = Field(min_length=1)
    external_ref: str = Field(min_length=1)
    pickup_address: str = Field(min_length=1)
    delivery_address: str = Field(min_length=1)
    requested_date: date
    lines: list[OrderLine] = Field(min_length=1)
    notes: str | None = None
    source: Source
    source_id: str = Field(min_length=1, description="File path or email Message-ID")
