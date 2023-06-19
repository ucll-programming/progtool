from pathlib import Path
from typing import Any
import yaml
import logging


class _MetadataReader:
    def read(self, path: Path) -> Any:
        logging.debug(f'Reading metadata at {path}')
        with open(path) as file:
            return yaml.safe_load(file)


_reader = _MetadataReader()


def read(path: Path) -> Any:
    return _reader.read(path)


TYPE_EXPLANATION = 'Explanation'
TYPE_EXERCISE = 'Exercise'
TYPE_SECTION = 'Section'
