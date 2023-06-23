from typing import Literal, Optional
from pydantic import BaseModel
from progtool.material import tree


NodeType = Literal['section'] | Literal['exercise'] | Literal['explanation']

Judgement = Literal['unknown'] | Literal['pass'] | Literal['fail']

class NodeRestData(BaseModel):
    name: str
    type: NodeType
    tree_path: tuple[str, ...]
    successor_tree_path: Optional[tuple[str, ...]]
    predecessor_tree_path: Optional[tuple[str, ...]]
    parent_tree_path: Optional[tuple[str, ...]]


class SectionRestData(NodeRestData):
    children: list[str]


class LeafRestData(NodeRestData):
    markdown: str


class ExplanationRestData(LeafRestData):
    pass


class ExerciseRestData(LeafRestData):
    judgement: Literal['unknown'] | Literal['pass'] | Literal['fail']
    difficulty: int


def judgement_to_string(judgement: tree.Judgement) -> Judgement:
    if judgement == tree.Judgement.UNKNOWN:
        return 'unknown'
    elif judgement == tree.Judgement.PASS:
        return 'pass'
    elif judgement == tree.Judgement.FAIL:
        return 'fail'
    else:
        raise RuntimeError(f'Unknown judgement {judgement}')
