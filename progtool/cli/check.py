from pathlib import Path
from progtool.material.metadata import load_metadata, ContentNodeMetadata
from progtool.material.navigator import MaterialNavigator
from progtool.material.tree import MaterialTreeBranch, build_tree, MaterialTreeNode, Section, Exercise, Explanation
from progtool.server.restdata import ExerciseRestData, ExplanationRestData, NodeRestData, SectionRestData, judgement_to_string
from progtool import repository
from rich.console import Console
from rich.table import Table
import logging
import click


@click.command()
def check() -> None:
    Checker().check()


class Checker:
    __root_path: Path
    __metadata: ContentNodeMetadata
    __tree: MaterialTreeNode
    __navigator: MaterialNavigator
    __console: Console

    def __init__(self):
        self.__root_path = repository.find_exercises_root()
        self.__metadata = load_metadata(self.__root_path)
        self.__tree = build_tree(self.__metadata)
        self.__navigator = MaterialNavigator(self.__tree)
        self.__console = Console()

    def check(self):
        self.__check_topics_order()

    def __check_topics_order(self):
        logging.info('Checking topics')
        current = self.__tree
        accumulated_topics = set()
        console = self.__console

        while (next := self.__navigator.find_successor_leaf(current)) is not None:
            for topic in next.topics.must_come_after:
                if topic not in accumulated_topics:
                    console.print(f"[red]Error[/red] Content node [blue]{next.tree_path}[/blue] requires [blue]{topic}[/blue] to have been discussed earlier")
            for topic in next.topics.must_come_before:
                if topic in accumulated_topics:
                    console.print(f"[red]Error[/red] Content node [blue]{next.tree_path}[/blue] requires [blue]{topic}[/blue] NOT to have been discussed earlier")
            for topic in next.topics.introduces:
                if topic in accumulated_topics:
                    console.print(f"[red]Error[/red] Content node [blue]{next.tree_path}[/blue] introduces [blue]{topic}[/blue], but this topic has already been introduced earlier")
                accumulated_topics.add(topic)

            current = next
