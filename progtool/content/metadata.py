from pathlib import Path
from typing import Callable, Iterable, Literal, Optional

import pydantic
import yaml

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


LinkPredicate = Callable[[LinkMetadata], bool]


def parse_metadata(path: Path, data: Any, link_predicate: LinkPredicate) -> Optional[ContentNodeMetadata]:
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
        if link_predicate(link_metadata):
            return load_metadata(path / link_metadata.location, link_predicate=link_predicate)
        else:
            return None
    elif node_type == TYPE_SECTION:
        identifier = data['id']
        name = data['name']
        children_objects = data['contents']
        if not isinstance(children_objects, list):
            raise MetadataError("A section's content should be a list")
        children = [
            child
            for child in (parse_metadata(path, child, link_predicate) for child in children_objects)
            if child is not None
        ]
        return SectionMetadata(
            id=identifier,
            name=name,
            type=TYPE_SECTION,
            contents=children,
            path=path,
        )
    else:
        raise MetadataError(f'Unrecognized node type {node_type}')


def load_metadata(root_path: Path, *, link_predicate: LinkPredicate) -> Optional[ContentNodeMetadata]:
    file_path = root_path / 'metadata.yaml'
    if not file_path.is_file():
        raise MetadataError(f'Could not read {file_path}')
    with file_path.open() as file:
        data = yaml.safe_load(file)
    return parse_metadata(root_path, data, link_predicate)


def load_everything(force_all: bool = False) -> LinkPredicate:
    def predicate(link: LinkMetadata):
        return link.available_by_default or force_all

    return predicate


def filter_by_tags(tags: Iterable[str]) -> LinkPredicate:
    def predicate(link: LinkMetadata) -> bool:
        if tags:
            return bool(link.tags & tag_set)
        else:
            return link.available_by_default

    tag_set = set(tags)
    return predicate
