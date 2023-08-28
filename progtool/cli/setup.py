from pathlib import Path
import github
import git
import logging
import sys
import re

from urllib.request import urlretrieve
from progtool.constants import *
import progtool.settings
from progtool.settings import Settings


def initialize(settings_file_path: Path):
    settings = load_existing_or_create_default_settings_file(settings_file_path)
    initialize_repository_root(settings_file_path, settings)
    initialize_html_path(settings_file_path, settings)


def initialize_html_path(settings_file_path: Path, settings: Settings) -> None:
    logging.info('Initializing HTML path')
    logging.debug('Checking if repository has HTML path setting')
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


def find_repository_root(directory: Path) -> Path:
    logging.info('Looking for git repository root starting in {directory}')
    repo = git.Repo(str(directory), search_parent_directories=True)

    logging.debug('Found a repository; getting root directory')
    root = Path(repo.git.rev_parse("--show-toplevel")).absolute()
    logging.debug(f'Determined that root directory is {root}')

    identifier_file_path = root / IDENTIFIER_FILE
    logging.debug(f'Looking for identifier file {identifier_file_path}')
    if not identifier_file_path.is_file():
        logging.critical("\n".join([
            f'Could not find identifier file {IDENTIFIER_FILE}',
            f"This either means you have removed it or that you're running this script in the wrong repository",
            f"Make sure to run it inside the course material repository",
            f"{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/missing-identifier-file.html"
        ]))
        sys.exit(ERROR_CODE_MISSING_IDENTIFIER_FILE)
    logging.debug(f'Found identifier file!')

    logging.debug(f'Checking contents of identifier file')
    contents = identifier_file_path.read_text()
    if contents != IDENTIFIER_FILE_CONTENTS:
        logging.critical("\n".join([
            f"The identifier file has the wrong contents",
            f"This is very surprising and really shouldn't happen."
            f"{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/wrong-identifier-file-contents.html"
        ]))
        sys.exit(ERROR_CODE_WRONG_IDENTIFIER_CONTENTS)
    logging.debug(f'Identifier file has right contents!')

    logging.info(f'Repository root directory is {root}')
    return root


# def create_settings_file(settings_file_path: Path, repository_root: Path) -> Settings:
#     settings = progtool.settings.create_default_settings(repository_root)
#     progtool.settings.write_settings_file(settings, settings_file_path)
#     return settings


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


# Using indices is roundabout way so as to not lose static typing
def find_index_of_latest_release(releases) -> int:
    def release_version(index):
        return parse_release_title(releases[index].title)

    return max(range(len(releases)), key=release_version)
