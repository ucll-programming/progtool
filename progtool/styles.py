import logging
from pathlib import Path
from urllib.request import urlretrieve

import github

from progtool.constants import DEFAULT_THEME_NAME, GITHUB_ORGANIZATION_NAME, GITHUB_THEMES_REPOSITORY_NAME


def download_default_style(destination_path: Path) -> None:
    download_style(DEFAULT_THEME_NAME, destination_path)


def download_style(theme_name: str, destination_path: Path) -> None:
    logging.info(f'Downloading theme {theme_name} to {destination_path}')

    url = determine_theme_url(theme_name)
    logging.debug('URL where style file should reside: {url}')

    logging.debug(f'Downloading {url} to {destination_path}')
    try:
        urlretrieve(url, str(destination_path))
    except Exception as e:
        logging.critical("Error occurred while downloading {url}")
        logging.critical(f"Error details: {e!r}")
        raise FailedDownload(url, destination_path)

    logging.info('Download completed successfully')


def determine_theme_url(theme_name: str) -> str:
    return find_theme(theme_name).url


class Theme:
    __name: str
    __url: str

    def __init__(self, name: str, url: str):
        self.__name = name
        self.__url = url

    @property
    def name(self) -> str:
        return self.__name

    @property
    def url(self) -> str:
        return self.__url

    def __str__(self) -> str:
        return f'Theme {self.name}'

    def __repr__(self) -> str:
        return f'Theme({self.name!r}, {self.url!r})'


def fetch_themes() -> list[Theme]:
    gh = github.Github()
    organization = gh.get_organization(GITHUB_ORGANIZATION_NAME)
    repository = organization.get_repo(GITHUB_THEMES_REPOSITORY_NAME)
    branch = repository.get_branch('master')
    files = branch.commit.files
    return [
        Theme(file.filename.rstrip('.scss'), file.raw_url)
        for file in files
        if file.filename.endswith('.scss')
    ]


def find_theme(name: str) -> Theme:
    themes = fetch_themes()
    for theme in themes:
        if theme.name == name:
            return theme
    raise NoSuchTheme(name)


class StylesException(Exception):
    pass


class FailedDownload(StylesException):
    def __init__(self, url: str, destination_path: Path):
        super().__init__(f'Failed to download from {url} to {destination_path}')

class NoSuchTheme(StylesException):
    def __init__(self, theme_name: str):
        super().__init__(f'No theme named {theme_name} found')
