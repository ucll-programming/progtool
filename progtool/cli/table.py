import logging
import sys
from typing import cast

import click
from rich.console import Console
from rich.tree import Tree

from progtool import settings
from progtool.cli.util import needs_settings
from progtool.content.metadata import (filter_by_tags, load_everything,
                                       load_metadata)
from progtool.content.navigator import ContentNavigator
from progtool.content.tree import (ContentNode, Exercise, Explanation, Section,
                                   build_tree)


@click.command()
@click.option("--tags", multiple=True, help="Show only nodes with specified tags")
@click.option("--all", "show_all", default=False, is_flag=True, help="Show all nodes, even those unavailable by default")
def table(tags: list[str], show_all: bool) -> None:
    """
    Prints out a tabular overview of all content
    """
    def create_link_predicate():
        if not tags:
            return load_everything(force_all=show_all)
        else:
            return filter_by_tags(tags)

    needs_settings() # type: ignore[call-arg]

    console = Console()
    tree = Tree('root')
    root_path = settings.repository_exercise_root()
    link_predicate = create_link_predicate()
    metadata = load_metadata(root_path, link_predicate=link_predicate)

    if metadata is None:
        console.print("[red]ERROR[/red] No nodes satisfy tags")
        sys.exit(-1)

    root = build_tree(metadata)
    print("| Name | Location |")
    print("| ---- | -------- |")
    for node in root.preorder_traversal():
        match node:
            case Section(name=name):
                print(f'| **{name}** | |')
            case Exercise(name=name, markdown_path=markdown_path):
                print(f'| {name} | {markdown_path.relative_to(root.local_path)} |')
            case Explanation(name=name, markdown_path=markdown_path):
                print(f'| {name} | {markdown_path.relative_to(root.local_path)} |')
