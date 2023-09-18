from pathlib import Path
import click

from progtool.cli.util import needs_settings


@click.group()
def settings() -> None:
    """
    Manage settings
    """
    pass


@settings.command()
@click.pass_context
def path(ctx: click.Context):
    """
    Show path of settings file.
    """
    settings_path: Path = ctx.obj['settings_path']
    print(settings_path)


@settings.command()
def fix() -> None:
    """
    Show path of settings file.
    """
    needs_settings(autofix=True) # type: ignore[call-arg]
