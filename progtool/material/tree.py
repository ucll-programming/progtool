from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from progtool.judging import Judge, create_judge
from progtool.material.treepath import TreePath
from progtool.material.metadata import ContentNodeMetadata, SectionMetadata, ExerciseMetadata, ExplanationMetadata
from progtool import settings
from enum import Enum
import asyncio
import logging


class MaterialError(Exception):
    pass


class Judgement(Enum):
    UNKNOWN = 0
    PASS = 1
    FAIL = -1


class MaterialTreeNode(ABC):
    __tree_path: TreePath
    __name: str

    def __init__(self, *, tree_path: TreePath, name: str):
        self.__tree_path = tree_path
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

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
    def judge_recursively(self, loop: asyncio.AbstractEventLoop) -> None:
        ...


class MaterialTreeLeaf(MaterialTreeNode):
    pass


class Explanation(MaterialTreeLeaf):
    __file: Path

    def __init__(self, *, tree_path: TreePath, name: str, file: Path):
        super().__init__(
            tree_path=tree_path,
            name=name
        )
        self.__file = file


    def __str__(self) -> str:
        return f'Explanation[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)

    @property
    def markdown(self) -> str:
        with open(self.__file) as file:
            return file.read()

    def judge_recursively(self, loop: asyncio.AbstractEventLoop) -> None:
        pass


class Exercise(MaterialTreeLeaf):
    judgement: Judgement

    __difficulty: int

    __assignment_file: Path

    __judge: Judge

    def __init__(self, *, tree_path: TreePath, name: str, difficulty: int, assignment_file: Path, judge: Judge):
        super().__init__(
            tree_path=tree_path,
            name=name
        )
        self.judgement = Judgement.UNKNOWN
        self.__difficulty = difficulty
        self.__assignment_file = assignment_file
        self.__judge = judge

    def __str__(self) -> str:
        return f'Exercise[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)

    @property
    def difficulty(self) -> int:
        return self.__difficulty

    @property
    def markdown(self) -> str:
        with open(self.__assignment_file) as file:
            return file.read()

    def judge(self, loop: asyncio.AbstractEventLoop) -> None:
        async def judge():
            logging.info(f'Judging exercise {self.tree_path}')
            tests_passed = await self.__judge.judge()
            judgement = Judgement.PASS if tests_passed else Judgement.FAIL
            logging.info(f'Exercise {self.tree_path}: {judgement}')
            self.judgement = judgement
        logging.info(f'Enqueueing exercise {self.tree_path}')
        loop.create_task(judge())

    def judge_recursively(self, loop: asyncio.AbstractEventLoop) -> None:
        self.judge(loop)


class MaterialTreeBranch(MaterialTreeNode):
    __children_table_value: dict[str, MaterialTreeNode]

    def __init__(self, *, name: str, tree_path: TreePath, children: list[MaterialTreeNode]):
        super().__init__(
            tree_path=tree_path,
            name=name,
        )
        self.__children_table_value = {
            child.tree_path.parts[-1]: child
            for child in children
        }

    def __getitem__(self, key: str) -> MaterialTreeNode:
        if key not in self.__children_table:
            raise MaterialError(f'{self.tree_path} has no child named "{key}"')
        return self.__children_table[key]

    @property
    def children(self) -> list[MaterialTreeNode]:
        return list(self.__children_table.values())

    @property
    def __children_table(self) -> dict[str, MaterialTreeNode]:
        return self.__children_table_value

    def judge_recursively(self, loop: asyncio.AbstractEventLoop) -> None:
        for child in self.children:
            child.judge_recursively(loop)


class Section(MaterialTreeBranch):
    def __init__(self, *, name: str, tree_path: TreePath, children: list[MaterialTreeNode]):
        super().__init__(
            name=name,
            tree_path=tree_path,
            children=children,
        )

    def __str__(self) -> str:
        return f'Section[{self.tree_path}]'

    def __repr__(self) -> str:
        return str(self)


def get_documentation_in_language(documentation: dict[str, str]):
    for language in settings.language_priority:
        if language in documentation:
            return documentation[language]
    raise MaterialError(f'Could not find material in right language')


def build_tree(metadata: ContentNodeMetadata) -> MaterialTreeNode:
    def recurse(metadata: ContentNodeMetadata, tree_path: TreePath):
        match metadata:
            case ExplanationMetadata(path=path, name=name, documentation=documentation):
                return Explanation(
                    tree_path=tree_path,
                    name=name,
                    file=path / get_documentation_in_language(documentation),
                )
            case ExerciseMetadata(path=path, name=name, difficulty=difficulty, documentation=documentation, judge=judge_metadata):
                judge = create_judge(path, judge_metadata)

                return Exercise(
                    tree_path=tree_path,
                    name=name,
                    difficulty=difficulty,
                    assignment_file=path / get_documentation_in_language(documentation),
                    judge=judge,
                )
            case SectionMetadata(path=path, name=name, contents=contents):
                children = [
                    recurse(child, tree_path / child.id)
                    for child in contents
                ]

                return Section(
                    name=name,
                    tree_path=tree_path,
                    children=children,
                )
            case _:
                raise MaterialError('Unknown metadata {metadata!r}')

    return recurse(metadata, TreePath())
