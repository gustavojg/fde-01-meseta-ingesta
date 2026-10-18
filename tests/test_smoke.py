from datetime import date

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from meseta_ingesta import __version__
from meseta_ingesta.cli import app
from meseta_ingesta.config import Settings
from meseta_ingesta.domain.models import Order, OrderLine, Source


def test_version_is_exposed() -> None:
    assert __version__


def test_settings_default_to_dry_run(settings: Settings) -> None:
    assert settings.dry_run is True
    assert settings.app_env == "dev"


def test_order_model_accepts_a_valid_order() -> None:
    order = Order(
        customer_code="CLI-001",
        external_ref="PED-2026-0001",
        pickup_address="Pol. Ind. Las Eras, Valladolid",
        delivery_address="C/ Mayor 1, Madrid",
        requested_date=date(2026, 10, 20),
        lines=[OrderLine(description="Palets", quantity=4, weight_kg=1200)],
        source=Source.EXCEL,
        source_id="samples/pedido.xlsx",
    )
    assert order.lines[0].quantity == 4


def test_order_model_rejects_empty_lines() -> None:
    with pytest.raises(ValidationError):
        Order(
            customer_code="CLI-001",
            external_ref="PED-2026-0002",
            pickup_address="A",
            delivery_address="B",
            requested_date=date(2026, 10, 20),
            lines=[],
            source=Source.EMAIL,
            source_id="<msg-id@example.com>",
        )


def test_cli_prints_version() -> None:
    result = CliRunner().invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
