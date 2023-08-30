from pathlib import Path
import click


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
