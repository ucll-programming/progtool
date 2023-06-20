from pathlib import Path
from typing import Any, Literal
import yaml
import logging
import pydantic


class NodeMetadata(pydantic.BaseModel):
    name: str
    type: Literal['exercise'] | Literal['explanation'] | Literal['section']


class SectionMetadata(NodeMetadata):
    pass


class ExerciseMetadata(NodeMetadata):
    pass


class ExplanationMetadata(NodeMetadata):
    pass


class _MetadataReader:
    def read(self, path: Path) -> NodeMetadata:
        logging.debug(f'Reading metadata at {path}')
        with open(path) as file:
            data = yaml.safe_load(file)
            type = data['type']
            if type == TYPE_EXPLANATION:
                return ExplanationMetadata.parse_obj(data)
            elif type == TYPE_EXERCISE:
                return ExerciseMetadata.parse_obj(data)
            elif type == TYPE_SECTION:
                return SectionMetadata.parse_obj(data)
            else:
                raise RuntimeError(f'Unrecognized type {type}')



_reader = _MetadataReader()


def read(path: Path) -> NodeMetadata:
    return _reader.read(path)


TYPE_EXPLANATION = 'explanation'
TYPE_EXERCISE = 'exercise'
TYPE_SECTION = 'section'
