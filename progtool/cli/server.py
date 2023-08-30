import sys
import click
import logging

from progtool.cli.util import needs_settings
from progtool.constants import TOOL_NAME


@click.command()
def server():
    """
    Set up server.
    """
    import progtool.server
    needs_settings()  # type: ignore[call-arg]
    progtool.server.run()
