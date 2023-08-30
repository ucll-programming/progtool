import click
from progtool.cli.util import needs_settings
from progtool.styles import download_style, download_default_style, fetch_themes
import progtool.settings as settings
from rich.console import Console
from rich.table import Table


@click.group()
def theme():
    """
    Manages themes
    """


@theme.command()
def default():
    """
    Downloads the default theme
    """
    needs_settings()
    download_default_style(settings.style_path())


@theme.command()
@click.argument('name')
def select(name):
    """
    Downloads a new theme
    """
    needs_settings()
    download_style(name, settings.style_path())


@theme.command()
def list():
    """
    Lists available themes
    """
    themes = fetch_themes()

    console = Console()
    table = Table()
    table.add_column('Version')
    table.add_column('URL')

    for theme in themes:
        table.add_row(theme.name, theme.url)

    console.print(table)
