import logging
import os
from pathlib import Path
from typing import Annotated, Optional
import yaml
import pydantic

SerializableFilePath = Annotated[pydantic.FilePath, pydantic.PlainSerializer(lambda path: str(path), return_type=str, when_used='always')]
SerializableDirectoryPath = Annotated[pydantic.FilePath, pydantic.PlainSerializer(lambda path: str(path), return_type=str, when_used='always')]


class Settings(pydantic.BaseModel):
    language_priorities: list[str]
    html_path: Optional[SerializableFilePath]
    repository_root: Optional[SerializableDirectoryPath]
    judgment_cache: Optional[SerializableFilePath]
    cache_delay: float

    # @pydantic.field_serializer()


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
    computer_name = os.environ['COMPUTERNAME']

    if computer_name == 'LT2180298':
        return Path('C:/repos/ucll/programming/frontend/dist/index.html')
    else:
        return Path('G:/repos/ucll/programming/frontend/dist/index.html')


def repository_root() -> Path:
    computer_name = os.environ['COMPUTERNAME']

    if computer_name == 'LT2180298':
        return Path('C:/repos/ucll/programming/course-material')
    else:
        return Path('G:/repos/ucll/programming/course-material')


def judgment_cache() -> Path:
    return Path(get_settings().judgment_cache)


def cache_delay() -> float:
    return get_settings().cache_delay
