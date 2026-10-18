"""Application settings, loaded from environment variables or a `.env` file.

See `.env.example` at the repository root for the full list and defaults.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # General
    app_env: Literal["dev", "staging", "prod"] = "dev"
    log_level: str = "INFO"
    dry_run: bool = True

    # Excel source
    excel_inbox_dir: Path = Path("./inbox")
    excel_processed_dir: Path = Path("./outbox/processed")
    excel_rejected_dir: Path = Path("./outbox/rejected")

    # Email source (IMAP)
    imap_host: str = "imap.example.com"
    imap_port: int = 993
    imap_user: str = ""
    imap_password: str = ""
    imap_folder: str = "INBOX"
    imap_poll_seconds: int = 60

    # ERP target
    erp_base_url: str = "https://erp.example.com/api"
    erp_api_key: str = ""
    erp_timeout_seconds: int = 30

    # Manual review queue
    review_notify_email: str = ""


def get_settings() -> Settings:
    return Settings()
