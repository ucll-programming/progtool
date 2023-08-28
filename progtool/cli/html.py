import logging
from typing import cast

import click
from rich.console import Console
from rich.tree import Tree
from progtool.cli.util import needs_settings

from progtool.content.metadata import (filter_by_tags, load_everything,
                                       load_metadata)
from progtool.content.tree import (ContentNode, Exercise, Explanation, Section,
                                   build_tree)
from progtool import settings


@click.group()
def html() -> None:
    """
    Manage HTML file
    """
    pass


@html.command()
def path():
    """
    Show path of html file.
    """
    needs_settings()
    print(settings.get_settings().html_path)


# @html.command()
# def version():
#     """
#     Determine version of local html file.
#     """
