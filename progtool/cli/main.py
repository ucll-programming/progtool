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
from progtool import settings

import sys
import os


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
@click.option('--config-file', default=lambda: os.environ.get("PROGTOOL_CONFIGURATION_PATH", str(settings.default_settings_path())))
def cli(verbose, log_file, config_file):
    _configure_logging(verbosity_level=verbose, log_file=log_file)

    config_file_path = Path(config_file)
    logging.info(f"Looking for configuration file {config_file_path}")
    if not config_file_path.is_file():
        logging.info(f"No configuration file found at {config_file_path}")
        setup.initialize(config_file_path)
        sys.exit(0)
    else:
        settings.load_settings(config_file_path)


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
