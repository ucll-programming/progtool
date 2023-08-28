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
from progtool.html import determine_version, fetch_list_of_releases

from rich.console import Console
from rich.table import Table


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
    print(settings.html_path())


@html.command()
def version():
    """
    Determine version of local html file.
    """
    needs_settings()
    version = determine_version(settings.html_path())
    print(".".join(str(number) for number in version))


@html.command()
def available():
    """
    Looks online for which HTML versions are available.
    """
    releases = fetch_list_of_releases()
    releases.sort(key=lambda release: release.version, reverse=True)

    console = Console()
    table = Table()
    table.add_column('Version')
    table.add_column('URL')

    for release in releases:
        version_string = ".".join(str(n) for n in release.version)
        table.add_row(version_string, release.url)

    console.print(table)
