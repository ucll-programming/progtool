from typing import Literal
from pydantic import BaseModel
from progtool.material import tree


NodeType = Literal['section'] | Literal['exercise'] | Literal['explanation']

Judgement = Literal['unknown'] | Literal['pass'] | Literal['fail']

class NodeData(BaseModel):
    name: str
    type: NodeType
    tree_path: tuple[str, ...]


class SectionData(NodeData):
    children: list[str]


class LeafData(NodeData):
    markdown: str


class ExplanationData(LeafData):
    pass


class ExerciseData(LeafData):
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
