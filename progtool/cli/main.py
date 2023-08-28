import logging
from pathlib import Path
from typing import Optional

import click
from rich.logging import RichHandler
from progtool.cli import setup

from progtool.cli.check import check
from progtool.cli.create import create
from progtool.cli.index import index
from progtool.cli.server import server
from progtool.cli.tree import tree
from progtool import constants, settings

import sys
import os

from progtool.result import Success, Failure


def _configure_verbosity(verbosity_level: Optional[int]) -> None:
    match verbosity_level:
        case 1:
            level = logging.INFO
        case 2:
            level = logging.DEBUG
        case _:
            level = logging.ERROR

    logging.basicConfig(
        handlers=[RichHandler()],
        level=level,
        force=True,
    )


def _configure_log_file(log_file: Optional[str]) -> None:
    if log_file:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)5s] [%(threadName)12s]: %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)



def _configure_logging(*, verbosity_level: Optional[int], log_file: Optional[str]) -> None:
    _configure_verbosity(verbosity_level)
    _configure_log_file(log_file)


@click.group()
@click.option('-v', '--verbose', count=True)
@click.option('--log-file', default=None)
@click.option('--settings', "settings_path_string", default=lambda: os.environ.get(constants.SETTINGS_FILE_ENVIRONMENT_VARIABLE, str(settings.default_settings_path())))
def cli(verbose: int, log_file: str, settings_path_string: str):
    _configure_logging(verbosity_level=verbose, log_file=log_file)

    settings_path = Path(settings_path_string)
    logging.info(f"Loading settings at {settings_path}")
    match settings.load_and_verify_settings(settings_path):
        case Success():
            # Settings have been stored in global variable, just proceed
            pass

        case Failure():
            logging.info(f"Could not load settings successfully; attempting to fix it")
            setup.initialize(settings_path)
            sys.exit(0)


def process_command_line_arguments():
    commands = [
        tree,
        server,
        index,
        create,
        check,
    ]

    for command in commands:
        cli.add_command(command)

    cli()
