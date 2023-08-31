from pathlib import Path
import click
from progtool.cli.util import needs_settings
import progtool.setup


@click.command()
@click.pass_context
def setup(ctx: click.Context):
    """
    Sets things up
    """
    settings_path: Path = ctx.obj['settings_path']
    print('Setting things up...')
    progtool.setup.initialize(settings_path)
    print('Checking...')
    needs_settings()  # type: ignore[call-arg]
    print('Successfully set things up')
