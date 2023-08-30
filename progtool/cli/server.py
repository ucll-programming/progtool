import sys
import click
import logging

from progtool.cli.util import needs_settings
from progtool.constants import TOOL_NAME
from progtool.html import new_html_version_available


@click.command()
def server(no_update_check: bool):
    """
    Set up server.
    """
    import progtool.server
    needs_settings()  # type: ignore[call-arg]
    progtool.server.run()
