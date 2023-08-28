import logging
import os
from pathlib import Path
from typing import Annotated, Optional
import yaml
import pydantic

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


def load_settings(path: Path):
    global _settings
    with open(path) as file:
        raw_data = yaml.safe_load(file)
    _settings = Settings.model_validate(raw_data)


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
