import click

from progtool.cli.settings import needs_settings


@click.command()
def server():
    """
    Set up server.
    """
    import progtool.server
    needs_settings()  # type: ignore[call-arg]
    progtool.server.run()
