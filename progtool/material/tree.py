from __future__ import annotations
from pathlib import Path
from typing import Optional
import logging
import os


class MaterialTreeNode:
    __path: Path

    def __init__(self, path: Path):
        self.__path = path

    @property
    def name(self) -> str:
        return self.__path.name

    @property
    def path(self) -> Path:
        return self.__path


class MaterialTreeLeaf(MaterialTreeNode):
    pass


class ExplanationLeaf(MaterialTreeLeaf):
    pass


class ExerciseLeaf(MaterialTreeLeaf):
    pass


class SectionNode(MaterialTreeNode):
    __children: dict[str, MaterialTreeNode]

    def __init__(self, path: Path):
        super().__init__(path)
        self.__children = None

    def __getitem__(self, key: str) -> MaterialTreeNode:
        return self.children[key]

    @property
    def children(self) -> dict[str, MaterialTreeNode]:
        if self.__children is None:
            self.__children = self.__compute_children()
        return self.__children

    def __compute_children(self) -> list[MaterialTreeNode]:
        entries = os.listdir(self.path)
        nodes = (_create_node(self.path / entry) for entry in entries) # Can contain None values
        return {node.name: node for node in nodes if node}


def _create_node(path: Path) -> Optional[MaterialTreeNode]:
    if _is_exercise_node(path):
        logging.debug(f'{path} recognized as exercise')
        return ExerciseLeaf(path)
    elif _is_explanations_node(path):
        logging.debug(f'{path} recognized as explanations')
        return ExplanationLeaf(path)
    elif _is_section_node(path):
        logging.debug(f'{path} recognized as section')
        return SectionNode(path)
    else:
        logging.debug(f'{path} not recognized as node')
        return None


def _is_exercise_node(path: Path) -> bool:
    return os.path.isfile(path / 'assignment.md')


def _is_explanations_node(path: Path) -> bool:
    return os.path.isfile(path / 'explanations.md')


def _is_section_node(path: Path) -> bool:
    return os.path.isfile(path / 'section.yaml')


def create_material_tree(root_path: Path) -> MaterialTreeNode:
    return _create_node(root_path)
