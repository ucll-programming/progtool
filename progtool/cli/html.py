import logging
import sys
from pathlib import Path
from typing import cast

import click
from rich.console import Console
from rich.table import Table

from progtool import constants, settings
from progtool.cli.util import needs_settings
from progtool.constants import (COURSE_MATERIAL_DOCUMENTATION_URL,
                                GITHUB_ORGANIZATION_NAME)
from progtool.html import (GitHubOrganizationNotFound,
                           determine_local_html_version, download_latest_html,
                           fetch_list_of_releases, find_latest_release)


@click.group()
def html() -> None:
    """
    Manage HTML file
    """
    pass


@html.command()
def path() -> None:
    """
    Show path of html file.
    """
    needs_settings() # type: ignore[call-arg]
    print(settings.html_path())


@html.command()
@click.argument("path", type=str)
@click.pass_context
def setpath(ctx: click.Context, path: str) -> None:
    """
    Sets path of html file.
    """
    logging.info("Loading settings")
    html_path = Path(path).absolute()

    if html_path.suffix != '.html':
        print(f'{html_path} should point to .html file')
        sys.exit(constants.ERROR_CODE_GENERIC)

    if not html_path.is_file():
        print(f'No file found with path {html_path}')
        sys.exit(constants.ERROR_CODE_GENERIC)

    settings_path: Path = cast(Path, ctx.obj['settings_path'])
    s = settings.load_settings(settings_path)
    s.html_path = Path(path)
    settings.write_settings_file(settings=s, path=settings_path)
    print(f'index.html path set to {html_path}')


@html.command()
def version() -> None:
    """
    Determine version of local html file.
    """
    needs_settings() # type: ignore[call-arg]
    version = determine_local_html_version(settings.html_path())
    print(version)


@html.command()
def available() -> None:
    """
    Looks online for which HTML versions are available.
    """
    try:
        releases = fetch_list_of_releases()
        releases.sort(key=lambda release: release.version, reverse=True)

        console = Console()
        table = Table()
        table.add_column('Version')
        table.add_column('URL')

        for release in releases:
            table.add_row(str(release.version), release.url)

        console.print(table)
    except GitHubOrganizationNotFound:
        logging.critical("\n".join([
            f'Could not find GitHub organization {GITHUB_ORGANIZATION_NAME}',
            f'{COURSE_MATERIAL_DOCUMENTATION_URL}/missing-github-organization.html'
        ]))


@html.command()
@click.option('--force', help='Downloads newest version regardless of version installed', is_flag=True, default=False)
def update(force: bool) -> None:
    """
    Updates to the latest HTML version
    """
    needs_settings() # type: ignore[call-arg]

    if force:
        should_download = True
    else:
        current_version = determine_local_html_version(settings.html_path())
        latest_release = find_latest_release()

        print(f'Currently installed version: {current_version}')
        print(f'Latest available version: {latest_release.version}')
        should_download = current_version < latest_release.version

    if should_download:
        print('Downloading latest version...')
        download_latest_html(settings.html_path())
        print('Done!')
    else:
        print('Latest version already installed')
