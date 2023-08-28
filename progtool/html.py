import logging
from pathlib import Path
import re
import sys
from typing import NamedTuple
from urllib.request import urlretrieve

import github

from progtool.constants import *
from progtool.version import Version


def find_url_of_latest_html() -> str:
    releases = fetch_list_of_releases()

    logging.debug(f'Looking for latest release')
    latest_release = find_latest_release(releases)
    logging.debug(f'Identified {latest_release.version} as latest release')

    return latest_release.url


class Release(NamedTuple):
    version: Version
    url: str


def fetch_list_of_releases() -> list[Release]:
    def get_organization():
        logging.debug(f'Looking for organization named {GITHUB_ORGANIZATION_NAME}')
        try:
            return gh.get_organization(GITHUB_ORGANIZATION_NAME)
        except Exception as e:
            logging.critical(f'An error occurred trying to find the GitHub organization {GITHUB_ORGANIZATION_NAME}: {e}')
            sys.exit(ERROR_CODE_GITHUB_ORGANIZATION_NOT_FOUND)

    def decode(release_data) -> Release:
        title = release_data.title
        version = Version.parse(title)
        assets = release_data.assets

        if len(assets) != 1:
            raise WrongNumberOfAssets(version, len(assets))

        asset = assets[0]
        url = asset.browser_download_url
        return Release(version, url)

    logging.info('Looking for latest version of index.html on GitHub')
    logging.debug('Creating GitHub instance')
    gh = github.Github()

    organization = get_organization()

    logging.debug(f'Looking for repository named {GITHUB_FRONTEND_REPOSITORY_NAME}')
    repository = organization.get_repo(GITHUB_FRONTEND_REPOSITORY_NAME)

    logging.debug(f'Fetching list of releases')
    releases = repository.get_releases()

    return [decode(release) for release in releases]


def find_latest_release(releases: list[Release]) -> Release:
    return max(releases, key=lambda release: release.version)


def download_html(target: Path) -> None:
    url = find_url_of_latest_html()
    download_file_to(url, target)


def download_file_to(url: str, target: Path) -> None:
    logging.info(f'Downloading {url} to {target}')
    urlretrieve(url, str(target))


def determine_html_version(html_path: Path) -> Version:
    logging.info(f'Determining version of html at {html_path}')
    if not html_path.is_file():
        logging.info(f'No file at {html_path}')
        raise RuntimeError()

    logging.debug(f'Reading content of {html_path}')
    html_source = html_path.read_text(encoding='utf-8')
    version_string = find_version_meta_element_in_html_source(html_source)
    return Version.parse(version_string)


def find_version_meta_element_in_html_source(html_source: str) -> str:
    regex = r'<meta\s+name="version"\s+content="(.*?)">'
    if not (match := re.search(regex, html_source)):
        raise NoVersionMetaElementFound()
    return match.group(1)


class HtmlException(Exception):
    pass


class NoVersionMetaElementFound(HtmlException):
    def __init__(self):
        super().__init__("Could not find version meta tag in HTML file")


class InvalidVersionString(HtmlException):
    def __init__(self, faulty_string: str):
        super().__init__(f"Could not parse {faulty_string} as version string")


class WrongNumberOfAssets(HtmlException):
    def __init__(self, release_version: Version, asset_count: int):
        super().__init__(f"Release {release_version} has unexpected number of assets ({asset_count})")
