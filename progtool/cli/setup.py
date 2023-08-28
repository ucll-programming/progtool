import logging
import re
import sys
from pathlib import Path
from typing import Any
from urllib.request import urlretrieve

import github
import yaml

import progtool.settings
from progtool.constants import *
from progtool.repository import find_repository_root
from progtool.settings import Settings


def initialize(settings_file_path: Path):
    settings = load_existing_or_create_default_settings_file(settings_file_path)
    initialize_repository_root(settings_file_path, settings)
    initialize_html_path(settings_file_path, settings)
    initialize_judgment_cache_path(settings_file_path, settings)


def initialize_judgment_cache_path(settings_file_path: Path, settings: Settings) -> None:
    logging.info('Initializing judgment cache path')
    logging.debug('Checking if judgment cache path is already set')
    if settings.judgment_cache is None:
        default_path = progtool.settings.default_judgment_cache_path()
        logging.debug(f'Judgment cache path not set; setting to default {default_path}')
        settings.judgment_cache = default_path
        progtool.settings.write_settings_file(settings=settings, path=settings_file_path)
    path = settings.judgment_cache
    logging.debug(f'Checking if judgment cache file exists at {path}')
    if not settings.judgment_cache.is_file():
        logging.debug(f'No file found with path {path}; creating it now')
        create_empty_judgment_cache(path)
    logging.info(f'Judgment cache exists at {path}')


def create_empty_judgment_cache(path: Path) -> None:
    data: dict[str, Any] = {}
    with path.open('w') as file:
        yaml.dump(data, file)


def initialize_html_path(settings_file_path: Path, settings: Settings) -> None:
    logging.info('Initializing HTML path')
    logging.debug('Checking if HTML path is set')
    if settings.html_path is None:
        logging.debug('No HTML path set; updating settings with default path ')
        settings.html_path = progtool.settings.default_html_path()
        progtool.settings.write_settings_file(settings=settings, path=settings_file_path)
        logging.debug(f'HTML path set to {settings.html_path}')
    html_path: Path = settings.html_path
    logging.debug(f'Checking if HTML path {settings.html_path} points to existing file')
    if not html_path.is_file():
        logging.debug(f'No file found with path {settings.html_path}; downloading it')
        download_html(html_path)
    logging.info(f'HTML file ready at {html_path}')


def initialize_repository_root(settings_file_path: Path, settings: Settings) -> None:
    logging.info('Initializing repository root')
    logging.debug('Checking if repository root setting exists')
    if settings.repository_root is None:
        current_directory = Path.cwd()
        logging.debug(f'No repository root set in settings file; looking for it starting in current directory {current_directory}')
        root_path = find_repository_root(current_directory)
        logging.debug(f'Updating settings file with repository root')
        settings.repository_root = root_path
        progtool.settings.write_settings_file(settings=settings, path=settings_file_path)
        logging.info('Found repository root and updated settings')
    else:
        logging.info('Root repository setting exists; leaving it at that')


def load_existing_or_create_default_settings_file(path: Path) -> Settings:
    logging.info(f'Looking for existing settings file at {path}')
    if not path.is_file():
        logging.info(f'No settings file found at {path}; creating one with default settings')
        settings: Settings = progtool.settings.create_default_settings()
        progtool.settings.write_settings_file(settings=settings, path=path)
    else:
        logging.info(f'Found existing settings file at {path}')
        settings = progtool.settings.load_settings(path)
    return settings





def download_html(target: Path):
    url = find_url_of_latest_html()
    download_file_to(url, target)


def download_file_to(url: str, target: Path) -> None:
    urlretrieve(url, str(target))


def find_url_of_latest_html() -> str:
    logging.info('Looking for latest version of index.html on GitHub')
    logging.debug('Creating GitHub instance')
    gh = github.Github()

    logging.debug(f'Looking for organization named {GITHUB_ORGANIZATION_NAME}')
    organization = gh.get_organization(GITHUB_ORGANIZATION_NAME)

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
