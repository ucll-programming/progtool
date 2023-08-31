import sys
import click
import logging

from progtool.cli.util import needs_settings
from progtool.constants import TOOL_NAME


@click.command()
@click.option('--debug', is_flag=True, default=False)
def server(debug):
    """
    Set up server.
    """
    import progtool.server
    needs_settings(autofix=True)  # type: ignore[call-arg]
    progtool.server.run(debug)
