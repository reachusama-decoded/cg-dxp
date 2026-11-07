from importlib.metadata import version as pkg_version
from typing import Optional

import typer

# IMPORTANT: Import export FIRST to patch ExportFormat before datacontract.cli loads
from . import export

from datacontract.cli import app as _datacontract_app

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.0.dev0"

_datacontract_version = pkg_version("datacontract-cli")

app = typer.Typer()


def _version_callback(value: bool):
    if value:
        typer.echo(f"datacounsel {__version__} (datacontract-cli {_datacontract_version})")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
):
    """datacounsel - Data contract management and export tooling."""
    if ctx.invoked_subcommand is None and not version:
        # Pass through to datacontract app
        _datacontract_app()


# Register all datacontract commands directly on our app
for command in _datacontract_app.registered_commands:
    app.registered_commands.append(command)

# Copy registered groups/sub-typers
for group in _datacontract_app.registered_groups:
    app.registered_groups.append(group)


@app.command("generate-migration")
def generate_migration_cmd(
    contract: str = typer.Argument(..., help="Path to ODCS contract YAML file (.odcs.yaml)"),
    output_dir: str = typer.Option(
        "migrations",
        "--output-dir",
        "-o",
        help="Output directory for Flyway migration files.",
    ),
    server: Optional[str] = typer.Option(
        None,
        "--server",
        "-s",
        help="Deprecated — no longer used. Will be removed in a future release.",
        hidden=True,
    ),
):
    """Generate a Flyway versioned migration SQL file from an ODCS data contract."""
    from .migration_generator import generate_migration

    migration_files = generate_migration(contract, output_dir=output_dir)
    for f in migration_files:
        typer.echo(f"Migration: {f}")


__all__ = ["__version__", "app", "export"]