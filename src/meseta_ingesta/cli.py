"""Command-line entry point: `meseta-ingesta --help`."""

from __future__ import annotations

import typer

from meseta_ingesta import __version__
from meseta_ingesta.config import get_settings

app = typer.Typer(help="Order ingestion from Excel and email into the ERP of Transportes Meseta.")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show the version and exit."),
) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def config() -> None:
    """Print the effective configuration (secrets masked)."""
    settings = get_settings()
    for key, value in settings.model_dump().items():
        if "password" in key or "api_key" in key:
            value = "***" if value else ""
        typer.echo(f"{key}={value}")


if __name__ == "__main__":
    app()
