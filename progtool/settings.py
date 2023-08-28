from enum import Enum, auto
import logging
import os
from pathlib import Path
from typing import Annotated, Optional
import yaml
import pydantic

from progtool.repository import RepositoryIdentifierResult, check_repository_identifier
from progtool.result import Result, Failure, Success

SerializableFilePath = Annotated[pydantic.FilePath, pydantic.PlainSerializer(lambda path: str(path), return_type=str, when_used='always')]
SerializableDirectoryPath = Annotated[pydantic.DirectoryPath, pydantic.PlainSerializer(lambda path: str(path), return_type=str, when_used='always')]


class Settings(pydantic.BaseModel):
    language_priorities: list[str]
    html_path: Optional[SerializableFilePath]
    repository_root: Optional[SerializableDirectoryPath]
    judgment_cache: Optional[SerializableFilePath]
    cache_delay: float


_settings: Optional[Settings]


def default_storage_path() -> Path:
    return (Path.home() / 'progtool').absolute()


def default_settings_path() -> Path:
    return default_storage_path() / 'progtool-settings.yaml'


def default_judgment_cache_path() -> Path:
    return default_storage_path() / "progtool-cache.json"


def default_html_path() -> Path:
    return default_storage_path() / "progtool-index.html"


def create_default_settings() -> Settings:
    return Settings(
        cache_delay=5,
        html_path=None,
        judgment_cache=None,
        language_priorities=['en', 'nl'],
        repository_root=None,
    )


def write_settings_file(*, settings: Settings, path: Path) -> None:
    logging.info(f"Writing settings file at {path}")

    parent = path.parent
    logging.debug(f'Checking if parent directory {parent} exists')
    if not parent.is_dir():
        logging.debug(f'Parent directory {parent} does not exist; creating it now')
        path.parent.mkdir(parents=True)
        logging.debug(f'Creating directory {parent}')

    logging.debug(f'Writing to {path}')
    with path.open('w') as file:
        yaml.dump(settings.model_dump(), file)
    logging.debug(f'Finished writing to {path}')



def load_settings(path: Path) -> Settings:
    with open(path) as file:
        logging.debug("Parsing yaml")
        raw_data = yaml.safe_load(file)
    return Settings.model_validate(raw_data)


class LoadSettingsResult(Enum):
    SUCCESS = auto()
    MISSING_SETTINGS_FILE = auto()
    SETTINGS_FILE_UNPARSABLE = auto()
    MISSING_HTML_SETTING = auto()
    MISSING_HTML_FILE = auto()
    MISSING_JUDGMENT_CACHE_SETTING = auto()
    MISSING_JUDGMENT_CACHE_FILE = auto()
    MISSING_REPOSITORY_ROOT_SETTING = auto()
    INVALID_REPOSITORY_ROOT = auto()


def load_and_verify_settings(path: Path) -> Result[None, LoadSettingsResult]:
    global _settings

    logging.info(f"Loading settings from {path}")

    logging.debug(f'Checking if {path} exists')
    if not path.is_file():
        logging.info(f'File {path} does not exist')
        return Failure(LoadSettingsResult.MISSING_SETTINGS_FILE)

    try:
        with open(path) as file:
            logging.debug("Parsing yaml")
            raw_data = yaml.safe_load(file)
    except Exception:
        logging.info(f'Failed to parse file {path}')
        return Failure(LoadSettingsResult.SETTINGS_FILE_UNPARSABLE)

    logging.debug('Validating contents of settings file')
    _settings = Settings.model_validate(raw_data)

    logging.debug('Checking if html_path is set')
    if _settings.html_path is None:
        logging.info(f'No html path set in {path}')
        return Failure(LoadSettingsResult.MISSING_HTML_SETTING)

    logging.debug('Checking if html file exists')
    if not _settings.html_path.is_file():
        logging.info(f'File {_settings.html_path} does not exist')
        return Failure(LoadSettingsResult.MISSING_HTML_FILE)

    logging.debug('Checking if judgment cache is set')
    if _settings.judgment_cache is None:
        logging.info(f'No judgment cache is set in {path}')
        return Failure(LoadSettingsResult.MISSING_JUDGMENT_CACHE_SETTING)

    logging.debug('Checking if judgment cache exists')
    if not _settings.judgment_cache.is_file():
        logging.info(f'Judgment cache {_settings.judgment_cache} does not exist')
        return Failure(LoadSettingsResult.MISSING_JUDGMENT_CACHE_FILE)

    logging.debug('Checking if repository root is set')
    if _settings.repository_root is None:
        logging.info('Repository root not set')
        return Failure(LoadSettingsResult.MISSING_REPOSITORY_ROOT_SETTING)

    logging.debug('Checking validity of repository root')
    if check_repository_identifier(_settings.repository_root) != RepositoryIdentifierResult.SUCCESS:
        logging.debug(f'Repository root {_settings.repository_root} is not a valid repository')
        return Failure(LoadSettingsResult.INVALID_REPOSITORY_ROOT)

    return Success(None)


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        logging.critical('Bug: settings not loaded')
        raise RuntimeError()
    else:
        return _settings


def language_priorities() -> list[str]:
    return get_settings().language_priorities


def html_path() -> Path:
    path = get_settings().html_path
    if path is None:
        raise RuntimeError('Incomplete settings')
    return path


def repository_root() -> Path:
    root = get_settings().repository_root
    if root is None:
        raise RuntimeError('Incomplete settings')
    return root


def repository_exercise_root() -> Path:
    return repository_root() / 'exercises'


def judgment_cache() -> Path:
    path = get_settings().judgment_cache
    if path is None:
        raise RuntimeError('Incomplete settings')
    return path


def cache_delay() -> float:
    return get_settings().cache_delay
