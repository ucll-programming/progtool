import logging
from typing import Literal, Optional
from pydantic import BaseModel
from progtool.content import tree as content
from progtool.content.navigator import ContentNavigator


RestTreePath = tuple[str, ...]

NodeType = Literal['section'] | Literal['exercise'] | Literal['explanation']


class Node(BaseModel):
    name: str
    type: NodeType
    tree_path: RestTreePath
    successor: Optional[RestTreePath]
    predecessor: Optional[RestTreePath]
    parent: Optional[RestTreePath]


class Section(Node):
    children: list[Node]


class Leaf(Node):
    markdown_url: str


class Explanation(Leaf):
    pass


class Exercise(Leaf):
    judgement_url: str
    difficulty: int



def convert_tree(root: content.ContentNode) -> Node:
    def format_tree_path_of(node: Optional[content.ContentNode]) -> Optional[RestTreePath]:
        if node is None:
            return None
        else:
            return node.tree_path.parts

    def markdown_url(tree_path: content.TreePath) -> str:
        return f'/api/v1/markdown/{"/".join(tree_path.parts)}'

    def judgement_url(tree_path: content.TreePath) -> str:
        return f'/api/v1/judgement/{"/".join(tree_path.parts)}'

    def convert(content_node: content.ContentNode) -> Node:
        predecessor = navigator.find_predecessor_leaf(content_node)
        successor = navigator.find_successor_leaf(content_node)
        parent = navigator.find_parent(content_node)

        match content_node:
            case content.Section(children=children):
                return Section(
                    type='section',
                    tree_path=content_node.tree_path.parts,
                    name=content_node.name,
                    children=[convert(child) for child in children],
                    successor=format_tree_path_of(successor),
                    predecessor=format_tree_path_of(predecessor),
                    parent=format_tree_path_of(parent),
                )
            case content.Explanation():
                return Explanation(
                    type='explanation',
                    tree_path=content_node.tree_path.parts,
                    name=content_node.name,
                    markdown_url=markdown_url(content_node.tree_path),
                    successor=format_tree_path_of(successor),
                    predecessor=format_tree_path_of(predecessor),
                    parent=format_tree_path_of(parent),
                )
            case content.Exercise(difficulty=difficulty):
                return Exercise(
                    type='exercise',
                    tree_path=content_node.tree_path.parts,
                    name=content_node.name,
                    markdown_url=markdown_url(content_node.tree_path),
                    difficulty=difficulty,
                    successor=format_tree_path_of(successor),
                    predecessor=format_tree_path_of(predecessor),
                    parent=format_tree_path_of(parent),
                    judgement_url=judgement_url(content_node.tree_path),
                )
            case _:
                raise RuntimeError(f"Unrecognized node type: {type(content_node)}")

    navigator = ContentNavigator(root)
    return convert(root)
