import click
from progtool.cli.util import needs_settings
from progtool.styles import download_style, download_default_style, fetch_themes
import progtool.settings as settings


@click.group()
def cache():
    """
    Manages judgment cache
    """


@cache.command()
def clear():
    """
    Clears the judgment cache
    """
    needs_settings()
    path = settings.judgment_cache()
    path.unlink()


@cache.command
def path():
    """
    Prints path of judgment cache
    """
    needs_settings()
    path = settings.judgment_cache()
    print(path)
