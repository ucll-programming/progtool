from typing import cast
from progtool.material.tree import Exercise, Section, Explanation
from progtool.material.tree import create_material_tree
from progtool.repository import find_exercises_root


def _print_tree(args):
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

    tree = create_material_tree(find_exercises_root())
    recurse(tree, 0)


def add_command_line_parser(subparser) -> None:
    parser = subparser.add_parser('tree', help='Print overview tree')
    parser.set_defaults(func=_print_tree)
