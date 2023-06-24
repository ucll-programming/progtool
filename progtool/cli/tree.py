from typing import cast
from progtool.material.metadata import load_metadata
from progtool.material.tree import Exercise, MaterialTreeNode, Section, Explanation, build_tree
from progtool.repository import find_exercises_root
import click
from rich.tree import Tree
from rich.console import Console


@click.command()
def tree() -> None:
    def recurse(node: MaterialTreeNode, tree: Tree):
        match node:
            case Section():
                section = cast(Section, node)
                subtree = tree.add(section.name)
                for child in section.children:
                    recurse(child, subtree)
            case Exercise():
                exercise = cast(Exercise, node)
                tree.add(f'[red]{exercise.name}[/red]')
            case Explanation():
                explanation = cast(Explanation, node)
                tree.add(f'[blue]{explanation.name}[/blue]')
            case _:
                assert False, 'Unrecognized node type'

    console = Console()
    tree = Tree('root')
    root_path = find_exercises_root()
    metadata = load_metadata(root_path)
    root = build_tree(metadata)
    recurse(root, tree)
    console.print(tree)
