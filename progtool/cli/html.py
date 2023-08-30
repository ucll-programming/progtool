from typing import cast

import click
from rich.console import Console
from progtool.cli.util import needs_settings

from progtool import settings
from progtool.html import determine_html_version, download_latest_html, fetch_list_of_releases, find_latest_release

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
    version = determine_html_version(settings.html_path())
    print(version)


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
        table.add_row(str(release.version), release.url)

    console.print(table)


@html.command()
def update():
    """
    Updates to the latest HTML version
    """
    needs_settings()

    current_version = determine_html_version(settings.html_path())
    latest_release = find_latest_release()

    print(f'Currently installed version: {current_version}')
    print(f'Latest available version: {latest_release.version}')

    if current_version < latest_release.version:
        print('Downloading latest version...')
        download_latest_html(settings.html_path)
        print('Done!')
    else:
        print('Latest version already installed')
