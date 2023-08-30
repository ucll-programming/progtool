import logging
from pathlib import Path
from typing import Optional

import click
from rich.logging import RichHandler

import progtool.cli
from progtool import constants, settings

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
@click.option('--settings', "settings_path_string", default=lambda: os.environ.get(constants.SETTINGS_FILE_ENVIRONMENT_VARIABLE, str(settings.default_settings_path())))
@click.pass_context
def cli(ctx: click.Context, verbose: int, log_file: str, settings_path_string: str):
    _configure_logging(verbosity_level=verbose, log_file=log_file)
    ctx.ensure_object(dict)
    ctx.obj['settings_path'] = Path(settings_path_string)


def process_command_line_arguments():
    commands = [
        progtool.cli.tree,
        progtool.cli.server,
        progtool.cli.index,
        progtool.cli.check,
        progtool.cli.html,
        progtool.cli.settings,
        progtool.cli.theme,
        progtool.cli.cache,
    ]

    for command in commands:
        cli.add_command(command)

    cli()
