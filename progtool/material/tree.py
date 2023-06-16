from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Literal, Optional
from progtool.material.treepath import TreePath
import logging
import os


NodeType = Literal['exercise'] | Literal['explanations'] | Literal['section']


class MaterialTreeNode(ABC):
    __path: Path
    __tree_path: TreePath

    def __init__(self, path: Path, tree_path: TreePath):
        self.__path = path
        self.__tree_path = tree_path

    @property
    def name(self) -> str:
        return self.__path.name

    @property
    def path(self) -> Path:
        return self.__path

    @property
    def tree_path(self) -> TreePath:
        return self.__tree_path

    @abstractmethod
    def __str__(self) -> str:
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...

    @abstractmethod
    def type(self) -> NodeType:
        ...


class MaterialTreeLeaf(MaterialTreeNode):
    pass


class Explanation(MaterialTreeLeaf):
    def __str__(self) -> str:
        return f'Explanation[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)

    def type(self) -> NodeType:
        return 'explanations'


class Exercise(MaterialTreeLeaf):
    def __str__(self) -> str:
        return f'Exercise[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)

    def type(self) -> NodeType:
        return 'exercise'


class MaterialTreeBranch(MaterialTreeNode):
    __children: Optional[dict[str, MaterialTreeNode]]

    def __init__(self, path: Path, tree_path: TreePath):
        super().__init__(path, tree_path)
        self.__children = None

    def __getitem__(self, key: str) -> MaterialTreeNode:
        return self.children[key]

    @property
    def children(self) -> dict[str, MaterialTreeNode]:
        if self.__children is None:
            self.__children = self.__compute_children()
        return self.__children

    def __compute_children(self) -> dict[str, MaterialTreeNode]:
        entries = os.listdir(self.path)
        nodes = (_create_node(self.path / entry, self.tree_path / entry) for entry in entries) # Can contain None values
        return {node.name: node for node in nodes if node}


class Section(MaterialTreeBranch):
    def __str__(self) -> str:
        return f'Section[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)

    def type(self) -> NodeType:
        return 'section'


def _create_node(path: Path, tree_path: TreePath) -> Optional[MaterialTreeNode]:
    if _is_exercise_node(path):
        logging.debug(f'{path} recognized as exercise')
        return Exercise(path, tree_path)
    elif _is_explanations_node(path):
        logging.debug(f'{path} recognized as explanations')
        return Explanation(path, tree_path)
    elif _is_section_node(path):
        logging.debug(f'{path} recognized as section')
        return Section(path, tree_path)
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
    empty_tree_path = TreePath()
    root = _create_node(root_path, empty_tree_path)
    assert root is not None, 'root_path points to an empty tree' # TODO: Make exception
    return root
