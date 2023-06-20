from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Literal, Optional, cast
from progtool.material.treepath import TreePath
import logging
import os
from progtool.material import metadata



class MaterialTreeNode(ABC):
    __path: Path
    __tree_path: TreePath

    @staticmethod
    def contains_metadata(path: Path) -> bool:
        return os.path.isfile(path / 'metadata.yaml')

    @staticmethod
    def load_metadata(path: Path) -> Any:
        return metadata.read(path / "metadata.yaml")

    @staticmethod
    def contains_node_of_type(path: Path, expected_type: str) -> bool:
        if MaterialTreeNode.contains_metadata(path):
            data = MaterialTreeNode.load_metadata(path)
            result = data['Type'] == expected_type
            logging.debug(f'{path}.type == ${expected_type} is ${result}')
            return result
        else:
            return False

    @staticmethod
    def create(path: Path, tree_path: TreePath) -> Optional[MaterialTreeNode]:
        if Section.test(path):
            return Section(path, tree_path)
        elif Exercise.test(path):
            return Exercise(path, tree_path)
        elif Explanation.test(path):
            return Explanation(path, tree_path)
        else:
            return None

    def __init__(self, path: Path, tree_path: TreePath):
        self.__path = path
        self.__tree_path = tree_path

    @property
    def name(self) -> str:
        parts = self.tree_path.parts
        if parts:
            return parts[-1]
        else:
            return ''

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


class MaterialTreeLeaf(MaterialTreeNode):
    pass


class Explanation(MaterialTreeLeaf):
    @staticmethod
    def test(path: Path) -> bool:
        return MaterialTreeNode.contains_node_of_type(path, metadata.TYPE_EXPLANATION)

    def __str__(self) -> str:
        return f'Explanation[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)

    @property
    def __markdown_path(self) -> Path:
        return self.path / 'explanation.md'

    @property
    def markdown(self) -> str:
        logging.debug(f'Opening ${self.__markdown_path}')
        with open(self.__markdown_path) as file:
            return file.read()


class Exercise(MaterialTreeLeaf):
    @staticmethod
    def test(path: Path) -> bool:
        return MaterialTreeNode.contains_node_of_type(path, metadata.TYPE_EXERCISE)

    def __str__(self) -> str:
        return f'Exercise[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)

    @property
    def __markdown_path(self) -> Path:
        return self.path / 'assignment.md'

    @property
    def markdown(self) -> str:
        with open(self.__markdown_path) as file:
            return file.read()


class MaterialTreeBranch(MaterialTreeNode):
    __children_table_value: Optional[dict[str, MaterialTreeNode]]

    def __init__(self, path: Path, tree_path: TreePath):
        super().__init__(path, tree_path)
        self.__children_table_value = None

    def __getitem__(self, key: str) -> MaterialTreeNode:
        return self.__children_table[key]

    @property
    def children(self) -> list[MaterialTreeNode]:
        return list(self.__children_table.values())

    @property
    def __children_table(self) -> dict[str, MaterialTreeNode]:
        if self.__children_table_value is None:
            self.__children_table_value = self.__compute_children()
        return self.__children_table_value

    def __compute_children(self) -> dict[str, MaterialTreeNode]:
        entries = os.listdir(self.path)
        nodes = (MaterialTreeNode.create(self.path / entry, self.tree_path / entry) for entry in entries) # Can contain None values
        return {node.tree_path.parts[-1]: node for node in nodes if node}


class Section(MaterialTreeBranch):
    __name: Optional[str]

    def __init__(self, path: Path, tree_path: TreePath):
        super().__init__(path, tree_path)
        self.__name = None

    @staticmethod
    def test(path: Path) -> bool:
        return MaterialTreeNode.contains_node_of_type(path, metadata.TYPE_SECTION)

    def __str__(self) -> str:
        return f'Section[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)

    @property
    def name(self) -> str:
        if self.__name is None:
            self.__read_metadata()
        assert self.__name is not None, "Bug: __read_metadata is expected to fill in the field"
        return self.__name

    def __read_metadata(self) -> None:
        data = MaterialTreeNode.load_metadata(self.path)
        self.__name = data['Name']


def create_material_tree(root_path: Path) -> MaterialTreeNode:
    empty_tree_path = TreePath()
    root = MaterialTreeNode.create(root_path, empty_tree_path)
    assert root is not None, 'root_path points to an empty tree' # TODO: Make exception
    return root
