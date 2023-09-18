import abc
from enum import Enum, auto
import logging
import os
from pathlib import Path
from typing import Annotated, Optional
import yaml
import pydantic

from progtool.repository import InvalidIdentifierFile, MissingIdentifierFile, check_repository_identifier


SerializablePath = Annotated[Path, pydantic.PlainSerializer(lambda path: str(path), return_type=str, when_used='always')]

class Settings(pydantic.BaseModel):
    language_priorities: list[str]
    html_path: Optional[SerializablePath] = None
    style_path: Optional[SerializablePath] = None
    repository_root: Optional[SerializablePath] = None
    judgment_cache: Optional[SerializablePath] = None
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


def default_style_path() -> Path:
    return default_storage_path() / "progtool-style.scss"


def create_default_settings() -> Settings:
    return Settings(
        cache_delay=5,
        html_path=None,
        style_path=None,
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
    logging.info(f"Loading settings from {path}")

    logging.debug(f'Checking if {path} exists')
    if not path.is_file():
        logging.info(f'File {path} does not exist')
        raise MissingSettingsFile(path)

    try:
        with open(path) as file:
            logging.debug("Parsing yaml")
            raw_data = yaml.safe_load(file)
    except Exception:
        logging.info(f'Failed to parse file {path}')
        raise UnparseableSettingsFile(path)

    logging.debug('Validating contents of settings file')
    try:
        return Settings.model_validate(raw_data)
    except Exception as e:
        raise InvalidSettings(e)


def verify_settings(settings: Settings) -> None:
    logging.debug('Checking if html_path is set')
    if settings.html_path is None:
        logging.info(f'No html path set')
        raise MissingHtmlSetting()

    logging.debug('Checking if html file exists')
    if not settings.html_path.is_file():
        logging.info(f'HTML file {settings.html_path} does not exist')
        raise MissingHtmlFile(settings.html_path)

    logging.debug('Checking if style path is set')
    if settings.style_path is None:
        logging.info(f'No style path set')
        raise MissingStyleSetting()

    logging.debug('Checking if style file exists')
    if not settings.style_path.is_file():
        logging.info(f'Style file {settings.style_path} does not exist')
        raise MissingStyleFile(settings.style_path)

    logging.debug('Checking if judgment cache is set')
    if settings.judgment_cache is None:
        logging.info(f'No judgment cache is set')
        raise MissingJudgmentCacheSetting()

    logging.debug('Checking if judgment cache exists')
    if not settings.judgment_cache.is_file():
        logging.info(f'Judgment cache {settings.judgment_cache} does not exist')
        raise MissingJudgmentCacheFile(settings.judgment_cache)

    logging.debug('Checking if repository root is set')
    if settings.repository_root is None:
        logging.info('Repository root not set')
        raise MissingRepositoryRootSetting()

    logging.debug('Checking validity of repository root')
    try:
        check_repository_identifier(settings.repository_root)
    except (MissingIdentifierFile, InvalidIdentifierFile) as e:
        logging.debug(f'Repository root {settings.repository_root} is not a valid repository: {str(e)}')
        raise InvalidRepositoryRoot(settings.repository_root)


def load_and_verify_settings(path: Path) -> None:
    global _settings
    _settings = load_settings(path)
    verify_settings(_settings)


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        logging.critical('Bug: settings not loaded; needs_settings() should have been called')
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


def style_path() -> Path:
    path = get_settings().style_path
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


class SettingsException(Exception, abc.ABC):
    pass

class MissingSettingsFile(SettingsException):
    def __init__(self, path: Path):
        super().__init__(f'Missing settings file at {path}')

class UnparseableSettingsFile(SettingsException):
    def __init__(self, path: Path):
        super().__init__(f'Could not parse file {path}')

class MissingHtmlSetting(SettingsException):
    def __init__(self):
        super().__init__(f'Missing html path setting in settings file')

class MissingHtmlFile(SettingsException):
    def __init__(self, path: Path):
        super().__init__(f'No html file found at {path}')

class MissingStyleSetting(SettingsException):
    def __init__(self):
        super().__init__(f'Missing style path setting in settings file')

class MissingStyleFile(SettingsException):
    def __init__(self, path: Path):
        super().__init__(f'No style file found at {path}')

class MissingJudgmentCacheSetting(SettingsException):
    def __init__(self):
        super().__init__(f'Missing judgment cache setting')

class MissingJudgmentCacheFile(SettingsException):
    def __init__(self, path: Path):
        super().__init__(f'No file found at {path}')

class MissingRepositoryRootSetting(SettingsException):
    def __init__(self):
        super().__init__(f'Missing repository root setting')

class InvalidRepositoryRoot(SettingsException):
    def __init__(self, path: Path):
        super().__init__(f'Invalid repository root {path}')
        self.path = path

class InvalidSettings(SettingsException):
    def __init__(self, cause: Exception):
        super().__init__(f'Settings file contained invalid entries: {cause}')
