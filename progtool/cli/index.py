import logging
import os

import click
from rich.console import Console
from rich.table import Table

from progtool.cli import util
from progtool.cli.util import (create_reindexing_mapping,
                               find_indexed_subdirectories)


@click.group(help='Assists with indexing directories')
def index():
    pass


@index.command()
@click.option('-f', '--force', is_flag=True, help='Performs renames')
def re(force: bool):
    """
    Reindex subdirectories
    """
    def rename(old_path: str, new_path: str) -> None:
        if old_path != new_path:
            logging.info(f'Renaming {old_path} to {new_path}')
            os.rename(old_path, new_path)
        else:
            logging.info(f'[red] Skipping {old_path}; it already has the right name')

    indexed_directories = find_indexed_subdirectories()
    mapping = create_reindexing_mapping(indexed_directories)

    if force:
        for original_name, new_name in mapping.items():
            rename(str(original_name), str(new_name))
        print('Done!')
    else:
        console = Console()
        table = Table(show_header=True, header_style="blue")
        table.add_column('original')
        table.add_column('reindexed')

        for original_name, new_name in mapping.items():
            table.add_row(str(original_name), str(new_name))

        console.print(table)
        console.print("Use -f option to actually perform the renames")


@index.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('-n', '--dry-run', help="Show what will happen without actually taking action", is_flag=True)
def add(directory: str, dry_run: bool):
    """
    Add index to unindexed subdirectory
    """
    def rename(old_name, new_name):
        if dry_run:
            print(f'Would rename {old_name} to {new_name}')
        else:
            os.rename(old_name, new_name)

    next_index = util.find_lowest_unused_index_in_directory()
    old_name = directory
    new_name = util.add_index_to_string(old_name, next_index)
    rename(old_name, new_name)


@index.command
@click.argument('start', type=int)
@click.option('-d', '--delta', type=int, default=1)
@click.option('-f', '--force', default=False, is_flag=True)
def shift(start: int, delta: int, force: bool):
    '''
    Shift indices by a a certain amount
    '''
    def rename(old_path: str, new_path: str) -> None:
        if old_path != new_path:
            logging.info(f'Renaming {old_path} to {new_path}')
            os.rename(old_path, new_path)
        else:
            logging.info(f'[red] Skipping {old_path}; it already has the right name')

    indexed_subdirs = util.find_indexed_subdirectories()
    selected_subdirs = [subdir for subdir in indexed_subdirs if util.index_of(subdir) >= start]
    rename_table = {
        subdir: util.replace_index_in_path(subdir, util.index_of(subdir) + delta)
        for subdir in selected_subdirs
    }
    if force:
        for original_name, new_name in rename_table.items():
            rename(str(original_name), str(new_name))
        print('Done!')
    else:
        console = Console()

        table = Table(show_header=True, header_style="blue")
        table.add_column('original')
        table.add_column('reindexed')

        for original_name, new_name in rename_table.items():
            table.add_row(str(original_name), str(new_name))

        console.print(table)
        console.print("Use -f option to actually perform the renames")
