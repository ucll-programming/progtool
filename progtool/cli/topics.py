from typing import cast
import click
from progtool import settings

from progtool.cli.util import needs_settings
from progtool.content.metadata import load_everything, load_metadata

from rich.console import Console
from rich.table import Table

from progtool.content.tree import ContentNode, Exercise, Explanation, Section, build_tree


@click.group()
def topics() -> None:
    """
    Manage topics
    """
    pass


@topics.command()
def overview():
    """
    Lists all topics
    """

    def recurse(node: ContentNode, table: Table):
        match node:
            case Section():
                section = cast(Section, node)
                for child in section.children:
                    recurse(child, table)
            case Exercise():
                exercise = cast(Exercise, node)
                if topics := exercise.topics.introduces:
                    table.add_row(exercise.name, ", ".join(exercise.topics.introduces))
            case Explanation():
                explanation = cast(Explanation, node)
                if topics := explanation.topics.introduces:
                    table.add_row(explanation.name, ", ".join(explanation.topics.introduces))
            case _:
                assert False, 'Unrecognized node type'

    needs_settings()

    root_path = settings.repository_exercise_root()
    link_predicate = load_everything(force_all=True)
    metadata = load_metadata(root_path, link_predicate=link_predicate)
    root = build_tree(metadata)

    console = Console()
    table = Table()
    table.add_column('Node')
    table.add_column('Topics')

    recurse(root, table)
    console.print(table)