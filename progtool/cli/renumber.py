from progtool.cli.util import find_numbered_subdirectories, create_renumbering_mapping
from itertools import count
from rich.console import Console
from rich.table import Table
import logging
import click
import os


def _rename(old_path: str, new_path: str) -> None:
    if old_path != new_path:
        logging.info(f'Renaming {old_path} to {new_path}')
        os.rename(old_path, new_path)
    else:
        logging.info(f'[red] Skipping {old_path}; it already has the right name')


@click.command(help='Renumber subdirectories')
@click.option('-f', '--force', is_flag=True, help='Performs renames')
def renumber(force: bool):
    console = Console()
    numbered_directories = find_numbered_subdirectories()
    mapping = create_renumbering_mapping(numbered_directories)

    if force:
        for original_name, new_name in mapping.items():
            _rename(original_name, new_name)
        print('Done!')
    else:
        table = Table(show_header=True, header_style="blue")
        table.add_column('original')
        table.add_column('renumbered')

        for original_name, new_name in mapping.items():
            table.add_row(original_name, new_name)

        console.print(table)
        console.print("Use -f option to actually perform renames")
