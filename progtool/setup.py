import logging
import sys
from pathlib import Path
from typing import Any

import yaml
from progtool.html import download_latest_html

import progtool.settings
from progtool.constants import *
from progtool.repository import InvalidIdentifierFile, MissingIdentifierFile, NoGitRepository, find_repository_root
from progtool.settings import Settings
from progtool.styles import download_default_style


def initialize(settings_file_path: Path):
    settings = load_existing_or_create_default_settings_file(settings_file_path)
    initialize_repository_root(settings_file_path, settings)
    initialize_html_path(settings_file_path, settings)
    initialize_style_path(settings_file_path, settings)
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
        logging.debug(f'HTML path set to {settings.html_path}')
        updated_settings_file = True
    else:
        updated_settings_file = False
    html_path: Path = settings.html_path

    logging.debug(f'Checking if HTML path {html_path} points to existing file')
    if not html_path.is_file():
        logging.debug(f'No file found with path {html_path}; downloading it')
        download_latest_html(html_path)

    # Needs to be done separately in case downloading HTML file fails
    if updated_settings_file:
        logging.debug('Writing settings file')
        progtool.settings.write_settings_file(settings=settings, path=settings_file_path)
    logging.info(f'HTML file ready at {html_path}')


def initialize_style_path(settings_file_path: Path, settings: Settings) -> None:
    logging.info('Initializing style path')
    logging.debug('Checking if style path is set')
    if settings.style_path is None:
        logging.debug('No style path set; updating settings with default path ')
        settings.style_path = progtool.settings.default_style_path()
        logging.debug(f'Style path set to {settings.style_path}')
        updated_settings_file = True
    else:
        updated_settings_file = False
    style_path: Path = settings.style_path

    logging.debug(f'Checking if style path {style_path} points to existing file')
    if not style_path.is_file():
        logging.debug(f'No file found with path {style_path}; downloading it')
        download_default_style(style_path)

    # Needs to be done separately in case downloading HTML file fails
    if updated_settings_file:
        logging.debug('Writing settings file')
        progtool.settings.write_settings_file(settings=settings, path=settings_file_path)
    logging.info(f'Style file ready at {style_path}')


def initialize_repository_root(settings_file_path: Path, settings: Settings) -> None:
    logging.info('Initializing repository root')
    logging.debug('Checking if repository root setting exists')
    if settings.repository_root is None:
        current_directory = Path.cwd()
        logging.debug(f'No repository root set in settings file; looking for it starting in current directory {current_directory}')
        try:
            root_path = find_repository_root(current_directory)
        except NoGitRepository:
            logging.critical("\n".join([
                f'There is no Git repository at {current_directory}',
                f'I also looked in all parent directories and found nothing',
                f'Make sure you have *cloned* the repository, not merely downloaded it',
                f"{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/no-git-repository.html"
            ]))
            sys.exit(ERROR_CODE_NO_GIT_REPOSITORY)
        except MissingIdentifierFile:
            logging.critical("\n".join([
                f'Could not find identifier file {IDENTIFIER_FILE}',
                f"This either means you have removed it or that you're running this script in the wrong repository",
                f"Make sure to run it inside the course material repository",
                f"{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/missing-identifier-file.html"
            ]))
            sys.exit(ERROR_CODE_MISSING_IDENTIFIER_FILE)
        except InvalidIdentifierFile:
            logging.critical("\n".join([
                f"The identifier file has the wrong contents",
                f"This is very surprising and really shouldn't happen."
                f"{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/wrong-identifier-file-contents.html"
            ]))
            sys.exit(ERROR_CODE_WRONG_IDENTIFIER_CONTENTS)

        logging.debug(f'Updating settings file with repository root')
        settings.repository_root = root_path
        progtool.settings.write_settings_file(settings=settings, path=settings_file_path)
        logging.info('Found repository root and updated settings')
    else:
        logging.info('Root repository setting exists')


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
