from pathlib import Path
from typing import Any, Literal
import yaml
import pydantic
import logging

from progtool.judging.judge import JudgeMetadata


class TopicsMetadata(pydantic.BaseModel):
    introduces: list[str] = pydantic.Field(default_factory=lambda: [])
    must_come_before: list[str] = pydantic.Field(default_factory=lambda: [])
    must_come_after: list[str] = pydantic.Field(default_factory=lambda: [])

    class Config:
        extra=pydantic.Extra.forbid


class NodeMetadata(pydantic.BaseModel):
    path: Path # Location (note: multiple nodes can share a single location). Used as base location for relative paths inside the node.
    type: Literal['exercise', 'explanation', 'section', 'link']


class LinkMetadata(NodeMetadata):
    location: Path
    tags: set[str] = pydantic.Field(default_factory=lambda: set())
    available_by_default: bool = True

    class Config:
        extra=pydantic.Extra.forbid


class ContentNodeMetadata(NodeMetadata):
    id: str
    name: str
    topics: TopicsMetadata = pydantic.Field(default_factory=lambda: TopicsMetadata())


class SectionMetadata(ContentNodeMetadata):
    contents: list[ContentNodeMetadata]

    class Config:
        extra=pydantic.Extra.forbid


class ExerciseMetadata(ContentNodeMetadata):
    difficulty: int

    # Maps languages to files, e.g. { 'en' => 'assignment.en.md', 'nl' => 'assignment.nl.md' }
    documentation: dict[str, str]

    judge: JudgeMetadata

    @pydantic.validator('difficulty')
    def check_difficulty_range(cls, value):
        if not 1 <= value <= 20:
            raise ValueError()
        else:
            return value

    class Config:
        extra=pydantic.Extra.forbid


class ExplanationMetadata(ContentNodeMetadata):
    documentation: dict[str, str]

    class Config:
        extra=pydantic.Extra.forbid


TYPE_EXPLANATION: Literal['explanation'] = 'explanation'
TYPE_EXERCISE: Literal['exercise'] = 'exercise'
TYPE_SECTION: Literal['section'] = 'section'
TYPE_LINK: Literal['link'] = 'link'


class MetadataError(Exception):
    pass


def parse_metadata(path: Path, data: Any) -> ContentNodeMetadata:
    if not isinstance(data, dict):
        raise MetadataError('Metadata should be dict at top level')
    if 'type' not in data:
        raise MetadataError('No type field found')
    data['path'] = path
    node_type = data['type']
    if node_type == TYPE_EXERCISE:
        return ExerciseMetadata.parse_obj(data)
    elif node_type == TYPE_EXPLANATION:
        return ExplanationMetadata.parse_obj(data)
    elif node_type == TYPE_LINK:
        link_metadata = LinkMetadata.parse_obj(data)
        return load_metadata(path / link_metadata.location)
    elif node_type == TYPE_SECTION:
        identifier = data['id']
        name = data['name']
        tags = data.get('tags', set())
        available_by_default = data.get('available_by_default', True)
        children_objects = data['contents']
        if not isinstance(children_objects, list):
            raise MetadataError("A section's content should be a list")
        children = [parse_metadata(path, child) for child in children_objects]
        return SectionMetadata(
            id=identifier,
            name=name,
            type=TYPE_SECTION,
            contents=children,
            path=path,
        )
    else:
        raise MetadataError(f'Unrecognized node type {node_type}')


def load_metadata(root_path: Path) -> ContentNodeMetadata:
    file_path = root_path / 'metadata.yaml'
    if not file_path.is_file():
        raise MetadataError(f'Could not read {file_path}')
    with file_path.open() as file:
        data = yaml.safe_load(file)
    return parse_metadata(root_path, data)
