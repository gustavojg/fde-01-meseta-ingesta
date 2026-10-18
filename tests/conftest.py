import pytest

from meseta_ingesta.config import Settings


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    """Settings isolated from any local `.env`."""
    monkeypatch.setenv("APP_ENV", "dev")
    monkeypatch.setenv("DRY_RUN", "true")
    return Settings(_env_file=None)
