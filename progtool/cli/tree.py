from typing import cast
from progtool.material.metadata import load_metadata
from progtool.material.tree import Exercise, Section, Explanation, build_tree
from progtool.repository import find_exercises_root
import click


def _print_tree(help='Show tree'):
    def recurse(node, indentation):
        match node:
            case Section():
                section = cast(Section, node)
                print(" " * indentation + section.name)
                for child in section.children:
                    recurse(child, indentation + 2)
            case Exercise():
                exercise = cast(Exercise, node)
                print(" " * indentation + exercise.name)
            case Explanation():
                explanation = cast(Explanation, node)
                print(" " * indentation + explanation.name)
            case _:
                assert False, 'Unrecognized node type'

    root_path = find_exercises_root()
    metadata = load_metadata(root_path)
    tree = build_tree(metadata)
    recurse(tree, 0)


@click.command()
def tree() -> None:
    _print_tree()
