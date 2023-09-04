from pathlib import Path
from typing import Any, Callable, Iterable, Literal, Optional

import logging
import pydantic
import yaml

from progtool.judging.judge import JudgeMetadata


class TopicsMetadata(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra='forbid')
    introduces: list[str] = pydantic.Field(default_factory=lambda: [])
    must_come_before: list[str] = pydantic.Field(default_factory=lambda: [])
    must_come_after: list[str] = pydantic.Field(default_factory=lambda: [])


class NodeMetadata(pydantic.BaseModel):
    path: Path # Location (note: multiple nodes can share a single location). Used as base location for relative paths inside the node.
    type: Literal['exercise', 'explanation', 'section', 'link']


class LinkMetadata(NodeMetadata):
    model_config = pydantic.ConfigDict(extra='forbid')
    location: Path
    tags: set[str] = pydantic.Field(default_factory=lambda: set())
    available_by_default: bool = True


class ContentNodeMetadata(NodeMetadata):
    id: str
    name: str
    topics: TopicsMetadata = pydantic.Field(default_factory=lambda: TopicsMetadata())


class SectionMetadata(ContentNodeMetadata):
    model_config = pydantic.ConfigDict(extra='forbid')
    contents: list[ContentNodeMetadata]


class ExerciseMetadata(ContentNodeMetadata):
    model_config = pydantic.ConfigDict(extra='forbid')

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


class ExplanationMetadata(ContentNodeMetadata):
    model_config = pydantic.ConfigDict(extra='forbid')

    documentation: dict[str, str]


TYPE_EXPLANATION: Literal['explanation'] = 'explanation'
TYPE_EXERCISE: Literal['exercise'] = 'exercise'
TYPE_SECTION: Literal['section'] = 'section'
TYPE_LINK: Literal['link'] = 'link'


class MetadataError(Exception):
    pass


LinkPredicate = Callable[[LinkMetadata], bool]


def parse_metadata(path: Path, metadata: Any, link_predicate: LinkPredicate) -> Optional[ContentNodeMetadata]:
    """
    Parses the data stored in parameter metadata.
    Parameter path contains the path from which the metadata originates.
    Parameter link_predicate selects which links to follow.
    """
    logging.info(f'Parsing metadata from {path}')
    if not isinstance(metadata, dict):
        raise MetadataError('Metadata should be dict')
    if 'type' not in metadata:
        raise MetadataError('No type field found')
    metadata['path'] = path
    node_type = metadata['type']
    if node_type == TYPE_EXERCISE:
        try:
            return ExerciseMetadata.model_validate(metadata)
        except:
            logging.error(f"Error occurred while parsing Exercise metadata from {path}")
            raise
    elif node_type == TYPE_EXPLANATION:
        try:
            return ExplanationMetadata.model_validate(metadata)
        except:
            logging.error(f"Error occurred while parsing Explanation metadata from {path}")
            raise
    elif node_type == TYPE_LINK:
        try:
            link_metadata = LinkMetadata.model_validate(metadata)
        except:
            logging.error(f"Error occurred while parsing Link metadata from {path}")
            raise
        if link_predicate(link_metadata):
            return load_metadata(path / link_metadata.location, link_predicate=link_predicate)
        else:
            return None
    elif node_type == TYPE_SECTION:
        identifier = metadata['id']
        name = metadata['name']
        children_objects = metadata['contents']
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
    logging.info(f'Loading {file_path}')
    if not file_path.is_file():
        raise MetadataError(f'Link to {file_path} does not exist')
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
