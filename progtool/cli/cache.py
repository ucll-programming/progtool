import click
from progtool.cli.util import needs_settings
import progtool.settings as settings


@click.group()
def cache() -> None:
    """
    Manages judgment cache
    """
    pass


@cache.command()
def clear() -> None:
    """
    Clears the judgment cache
    """
    needs_settings()  # type: ignore[call-arg]
    path = settings.judgment_cache()
    path.unlink()


@cache.command
def path() -> None:
    """
    Prints path of judgment cache
    """
    needs_settings()  # type: ignore[call-arg]
    path = settings.judgment_cache()
    print(path)
