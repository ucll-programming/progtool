from typing import cast
from progtool.content.metadata import filter_by_tags, load_everything, load_metadata
from progtool.content.tree import Exercise, ContentNode, Section, Explanation, build_tree
from progtool.repository import find_exercises_root
import click
import logging
from rich.tree import Tree
from rich.console import Console


@click.command()
@click.option("--tags", multiple=True, help="Show only nodes with specified tags")
@click.option("--all", "show_all", default=False, is_flag=True, help="Show all nodes, even those unavailable by default")
def tree(tags, show_all) -> None:
    def recurse(node: ContentNode, tree: Tree):
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

    def create_link_predicate():
        if not tags:
            return load_everything(force_all=show_all)
        else:
            return filter_by_tags(tags)

    console = Console()
    tree = Tree('root')
    root_path = find_exercises_root()
    link_predicate = create_link_predicate()
    metadata = load_metadata(root_path, link_predicate=link_predicate)

    if metadata is None:
        console.print("[red]ERROR[/red] No nodes satisfy tags")
    else:
        root = build_tree(metadata)
        recurse(root, tree)
        console.print(tree)
