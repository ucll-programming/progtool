from collections import namedtuple
import logging
from pathlib import Path
import re
import sys
from typing import NamedTuple
from urllib.request import urlretrieve

import github

from progtool.constants import *


def find_url_of_latest_html() -> str:
    def get_organization():
        logging.debug(f'Looking for organization named {GITHUB_ORGANIZATION_NAME}')
        try:
            return gh.get_organization(GITHUB_ORGANIZATION_NAME)
        except Exception as e:
            logging.critical(f'An error occurred trying to find the GitHub organization {GITHUB_ORGANIZATION_NAME}: {e}')
            sys.exit(ERROR_CODE_GITHUB_ORGANIZATION_NOT_FOUND)

    logging.info('Looking for latest version of index.html on GitHub')
    logging.debug('Creating GitHub instance')
    gh = github.Github()

    organization = get_organization()

    logging.debug(f'Looking for repository named {GITHUB_FRONTEND_REPOSITORY_NAME}')
    repository = organization.get_repo(GITHUB_FRONTEND_REPOSITORY_NAME)

    logging.debug(f'Fetching list of releases')
    releases = list(repository.get_releases())
    logging.debug(f'Found {len(releases)} release(s): {" ".join(release.title for release in releases)}')

    logging.debug(f'Looking for latest release')
    latest_release_index = find_index_of_latest_release(releases)
    latest_release = releases[latest_release_index]
    logging.debug(f'Identified {latest_release.title} as latest release')

    logging.debug(f'Getting assets associated with release {latest_release.title}')
    assets = list(latest_release.get_assets())
    logging.debug(f'Found {len(assets)} asset(s)')

    if len(assets) != 1:
        logging.critical("\n".join([
            f'Latest version has unexpected amount of assets associated with it {(len(assets))}; only expected 1',
            f'This problem should be fixed by lectures',
            f'For now, you should download the index.html file manually; instructions can be find online',
            f'{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/manual-html-download.html'
        ]))
        sys.exit(ERROR_CODE_MULTIPLE_ASSETS_IN_RELEASE)

    asset = assets[0]
    url = asset.browser_download_url
    logging.info(f'URL found: {url}')

    return url


Version = tuple[int, int, int]

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
        version = parse_release_version_string(title)
        url = release_data.assets[0].browser_download_url
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


def parse_release_version_string(title: str) -> Version:
    regex = r'v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)'
    if match := re.fullmatch(regex, title):
        groups = match.groupdict()
        major = int(groups['major'])
        minor = int(groups['minor'])
        patch = int(groups['patch'])
        return (major, minor, patch)
    else:
        raise InvalidVersionString(f'Could not parse release title {title}; expected vN.N.N')


def parse_html_version_string(version_string: str) -> tuple[int, int, int]:
    return parse_release_version_string(f'v{version_string}')


# Using indices is roundabout way to not lose static typing
def find_index_of_latest_release(releases) -> int:
    def release_version(index):
        return parse_release_version_string(releases[index].title)

    return max(range(len(releases)), key=release_version)


def download_html(target: Path):
    url = find_url_of_latest_html()
    download_file_to(url, target)


def download_file_to(url: str, target: Path) -> None:
    logging.info(f'Downloading {url} to {target}')
    urlretrieve(url, str(target))


def determine_version(html_path: Path) -> tuple[int, int, int]:
    logging.info(f'Determining version of html at {html_path}')
    if not html_path.is_file():
        logging.info(f'No file at {html_path}')
        raise RuntimeError()

    logging.debug(f'Reading content of {html_path}')
    html_source = html_path.read_text(encoding='utf-8')
    version_string = find_version_meta_element_in_html_source(html_source)
    return parse_html_version_string(version_string)


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
