import click
import logging
from typing import Optional
from progtool.cli.tree import tree
from progtool.cli.server import server
from progtool.cli.create import create
from progtool.cli.index import index
from progtool.cli.check import check
from rich.logging import RichHandler


def configure_logging(*, verbosity_level: Optional[int], log_file: Optional[str]) -> None:
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

    if log_file:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)5s] [%(threadName)12s]: %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)




@click.group()
@click.option('-v', '--verbose', count=True)
@click.option('--log-file', default=None)
def cli(verbose, log_file):
    configure_logging(verbosity_level=verbose, log_file=log_file)


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
