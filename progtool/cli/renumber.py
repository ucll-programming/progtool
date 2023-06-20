from itertools import count
from rich.console import Console
from rich.table import Table
import logging
import os
import re


def _is_numbered(string: str) -> bool:
    """
    Checks if string starts with a number prefix.
    """
    return bool(re.fullmatch(r'\d+(-.+)?', string))


def _is_numbered_directory(path: str) -> bool:
    """
    Checks if path refers to a directory and its name is numbered.
    """
    return _is_numbered(path) and os.path.isdir(path)


def _remove_number(string: str) -> str:
    """
    Removes the number prefix from the string.
    """
    return re.sub(r'^\d+-?', '', string)


def _add_number(string: str, number: int) -> str:
    number_string = str(number).rjust(2, '0')

    if len(string) == 0:
        return number_string
    else:
        return f'{number_string}-{string}'


def _create_renumbering_mapping(strings: list[str]) -> dict[str, str]:
    sorted_strings = sorted(strings)
    renumbered_strings = {
        string: _add_number(_remove_number(string), index)
        for index, string in zip(count(start=1), sorted_strings)
    }
    return renumbered_strings


def _find_numbered_subdirectories() -> list[str]:
    return [entry for entry in os.listdir() if _is_numbered_directory(entry)]


def _rename(old_path: str, new_path: str) -> None:
    if old_path != new_path:
        logging.info(f'Renaming {old_path} to {new_path}')
        os.rename(old_path, new_path)
    else:
        logging.info(f'Skipping {old_path}; it already has the right name')
    print('Done!')


def _renumber(args):
    console = Console()
    numbered_directories = _find_numbered_subdirectories()
    mapping = _create_renumbering_mapping(numbered_directories)

    if args.force:
        for original_name, new_name in mapping.items():
            _rename(original_name, new_name)
    else:
        table = Table(show_header=True, header_style="blue")
        table.add_column('original')
        table.add_column('renumbered')

        for original_name, new_name in mapping.items():
            table.add_row(original_name, new_name)

        console.print(table)
        console.print("Use -f option to actually perform renames")



def add_command_line_parser(subparser) -> None:
    parser = subparser.add_parser('renumber', help='Renumber nodes in current directory')
    parser.add_argument('-f', action='store_true', dest='force', help='Needed to actually perform renames')
    parser.set_defaults(func=_renumber)
