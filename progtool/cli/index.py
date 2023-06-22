from progtool.cli.util import find_indexed_subdirectories, create_reindexing_mapping
from rich.console import Console
from rich.table import Table
import logging
import click
import os


@click.group(help='Assists with indexing directories')
def index():
    pass


@index.command(help='Reindex subdirectories')
@click.option('-f', '--force', is_flag=True, help='Performs renames')
def re(force):
    console = Console()
    indexed_directories = find_indexed_subdirectories()
    mapping = create_reindexing_mapping(indexed_directories)

    if force:
        for original_name, new_name in mapping.items():
            _rename(original_name, new_name)
        print('Done!')
    else:
        table = Table(show_header=True, header_style="blue")
        table.add_column('original')
        table.add_column('reindexed')

        for original_name, new_name in mapping.items():
            table.add_row(original_name, new_name)

        console.print(table)
        console.print("Use -f option to actually perform renames")


def _rename(old_path: str, new_path: str) -> None:
    if old_path != new_path:
        logging.info(f'Renaming {old_path} to {new_path}')
        os.rename(old_path, new_path)
    else:
        logging.info(f'[red] Skipping {old_path}; it already has the right name')
