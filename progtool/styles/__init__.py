import logging
from pathlib import Path
from urllib.request import urlretrieve

from progtool.constants import DEFAULT_THEME_NAME, GITHUB_ORGANIZATION_NAME, GITHUB_THEMES_REPOSITORY_NAME


def download_default_style(destination_path: Path) -> None:
    download_style(DEFAULT_THEME_NAME, destination_path)


def download_style(theme_name: str, destination_path: Path) -> None:
    logging.info(f'Downloading theme {theme_name} to {destination_path}')

    url = determine_theme_url(theme_name)
    logging.debug('URL where style file should reside: {url}')

    logging.debug(f'Downloading {url} to {destination_path}')
    urlretrieve(url, str(destination_path))

    logging.info('Download completed successfully')


def determine_theme_url(theme_name: str) -> str:
    return f'https://github.com/{GITHUB_ORGANIZATION_NAME}/{GITHUB_THEMES_REPOSITORY_NAME}/blob/master/{theme_name}.scss'


class StylesException(Exception):
    pass


class FailedStyleDownload(StylesException):
    def __init__(self, url: str, destination_path: Path):
        super().__init__(f'Failed to download from {url} to {destination_path}')
