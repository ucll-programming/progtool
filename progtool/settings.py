import os
from pathlib import Path
from typing import Optional
import yaml
import pydantic


class Settings(pydantic.BaseModel):
    language_priorities: list[str]
    html_path: Optional[str]
    repository_root: Optional[str]
    judgment_cache: str


def settings_path() -> Path:
    return Path.home() / 'progtool-settings.yaml'


def create_settings_file() -> None:
    with settings_path().open('w') as file:
        yaml.dump(default_settings(), file)


def default_settings():
    return Settings(
        language_priorities=['en', 'nl'],
        html_path=None,
        repository_root=None,
        judgment_cache=default_judgment_cache_path()
    )


def load_settings():
    path = settings_path()
    if not path.exists():
        create_settings_file()
    with open(path) as file:
        raw_settings = yaml.load(file)
        return Settings.model_validate(raw_settings)



def language_priorities():
    return ['en', 'nl']


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


def default_judgment_cache_path() -> Path:
    return Path.home() / "progtool-cache.json"


def judgment_cache() -> Path:
    return default_judgment_cache_path()


def cache_delay() -> float:
    return 5
