from typing import Literal
from pydantic import BaseModel


NodeType = Literal['section'] | Literal['exercise'] | Literal['explanation']


class NodeData(BaseModel):
    name: str
    type: NodeType
    path: str
    tree_path: tuple[str, ...]


class SectionData(NodeData):
    children: list[str]


class LeafData(NodeData):
    markdown: str


class ExplanationData(LeafData):
    pass


class ExerciseData(LeafData):
    pass
