from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import logging
import os


class MaterialTreeNode(ABC):
    __path: Path
    __tree_path: tuple[str, ...]

    def __init__(self, path: Path, tree_path: tuple[str, ...]):
        self.__path = path
        self.__tree_path = tuple(tree_path)

    @property
    def name(self) -> str:
        return self.__path.name

    @property
    def path(self) -> Path:
        return self.__path

    @property
    def tree_path(self) -> tuple[str, ...]:
        return self.__tree_path

    @abstractmethod
    def __str__(self) -> str:
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...


class MaterialTreeLeaf(MaterialTreeNode):
    pass


class ExplanationLeaf(MaterialTreeLeaf):
    def __str__(self) -> str:
        return f'Explanation[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)


class ExerciseLeaf(MaterialTreeLeaf):
    def __str__(self) -> str:
        return f'Exercise[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)


class SectionNode(MaterialTreeNode):
    __children: dict[str, MaterialTreeNode]

    def __init__(self, path: Path, tree_path: tuple[str, ...]):
        super().__init__(path, tree_path)
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
        nodes = (_create_node(self.path / entry, (*self.tree_path, entry)) for entry in entries) # Can contain None values
        return {node.name: node for node in nodes if node}

    def __str__(self) -> str:
        return f'Section[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)


def _create_node(path: Path, tree_path: tuple[str, ...]) -> Optional[MaterialTreeNode]:
    if _is_exercise_node(path):
        logging.debug(f'{path} recognized as exercise')
        return ExerciseLeaf(path, tree_path)
    elif _is_explanations_node(path):
        logging.debug(f'{path} recognized as explanations')
        return ExplanationLeaf(path, tree_path)
    elif _is_section_node(path):
        logging.debug(f'{path} recognized as section')
        return SectionNode(path, tree_path)
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
    empty_tree_path: tuple[str, ...] = tuple()
    return _create_node(root_path, empty_tree_path)
