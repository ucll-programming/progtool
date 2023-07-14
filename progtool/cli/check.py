import logging
from pathlib import Path

import click
from rich.console import Console

from progtool import repository
from progtool.content.metadata import (ContentNodeMetadata, ExerciseMetadata,
                                       ExplanationMetadata, SectionMetadata,
                                       load_everything, load_metadata)
from progtool.content.navigator import ContentNavigator
from progtool.content.tree import ContentNode, build_tree


@click.group(help="Checks content for mistakes")
def check() -> None:
    pass


@check.command(help="Verifies files")
def files() -> None:
    error_count = Checker().check_files()
    print(f"{error_count} error(s) found")


@check.command(help="Verifies topics")
def topics() -> None:
    error_count = Checker().check_topics_order()
    print(f"{error_count} error(s) found")


@check.command(help="Full verification")
def all() -> None:
    error_count = Checker().check_everything()
    print(f"{error_count} error(s) found")



class CheckerError(Exception):
    pass


class Checker:
    __root_path: Path
    __metadata: ContentNodeMetadata
    __tree: ContentNode
    __navigator: ContentNavigator
    __console: Console
    __error_count: int

    def __init__(self):
        self.__root_path = repository.find_exercises_root()
        metadata = load_metadata(self.__root_path, link_predicate=load_everything(force_all=True))
        if metadata is None:
            raise CheckerError("No nodes loaded")
        self.__metadata = metadata
        self.__tree = build_tree(self.__metadata)
        self.__navigator = ContentNavigator(self.__tree)
        self.__console = Console()
        self.__error_count = 0

    def check_everything(self):
        self.check_topics_order()
        self.check_files()
        return self.__error_count

    def check_topics_order(self):
        """
        Checks the constraints on topic order
        """
        logging.info('Checking topics')
        current = self.__tree
        accumulated_topics = set()

        while (next := self.__navigator.find_successor_leaf(current)) is not None:
            for topic in next.topics.must_come_after:
                if topic not in accumulated_topics:
                    self.__report_error(f"Content node [blue]{next.tree_path}[/blue] requires [blue]{topic}[/blue] to have been discussed earlier")
            for topic in next.topics.must_come_before:
                if topic in accumulated_topics:
                    self.__report_error(f"Content node [blue]{next.tree_path}[/blue] requires [blue]{topic}[/blue] NOT to have been discussed earlier")
            for topic in next.topics.introduces:
                if topic in accumulated_topics:
                    self.__report_error(f"Content node [blue]{next.tree_path}[/blue] introduces [blue]{topic}[/blue], but this topic has already been introduced earlier")
                accumulated_topics.add(topic)

            current = next

        return self.__error_count

    def check_files(self):
        """
        Checks that all files mentioned in metadata exist.
        """
        logging.info('Checking files')
        self.__check_files_recursively(self.__metadata)
        return self.__error_count

    def __check_files_recursively(self, node: ContentNodeMetadata):
        match node:
            case SectionMetadata(contents=children):
                for child in children:
                    self.__check_files_recursively(child)
            case ExplanationMetadata(documentation=documentation, path=path):
                for file in documentation.values():
                    expected_file = path / file
                    if not expected_file.is_file():
                        self.__report_error(f"File {expected_file} does not exist")
            case ExerciseMetadata(documentation=documentation, path=path):
                for file in documentation.values():
                    expected_file = path / file
                    if not expected_file.is_file():
                        self.__report_error(f"File {expected_file} does not exist")

    def __report_error(self, message: str) -> None:
        self.__console.print(f"[red]Error[/red] {message}")
        self.__error_count += 1