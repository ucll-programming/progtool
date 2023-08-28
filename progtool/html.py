import logging
from pathlib import Path
import re
import sys
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


def parse_release_title(title: str) -> tuple[int, int, int]:
    regex = r'v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)'
    if match := re.fullmatch(regex, title):
        groups = match.groupdict()
        major = int(groups['major'])
        minor = int(groups['minor'])
        patch = int(groups['patch'])
        return (major, minor, patch)
    else:
        raise ValueError(f'Could not parse release title {title}; expected vN.N.N')


# Using indices is roundabout way to not lose static typing
def find_index_of_latest_release(releases) -> int:
    def release_version(index):
        return parse_release_title(releases[index].title)

    return max(range(len(releases)), key=release_version)


def download_html(target: Path):
    url = find_url_of_latest_html()
    download_file_to(url, target)


def download_file_to(url: str, target: Path) -> None:
    logging.info(f'Downloading {url} to {target}')
    urlretrieve(url, str(target))
