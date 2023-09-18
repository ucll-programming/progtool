import logging
import os
import re
import sys
from itertools import count
from pathlib import Path
from typing import Optional

import click

from progtool import settings
from progtool import setup
from progtool.constants import COURSE_MATERIAL_DOCUMENTATION_URL, ERROR_CODE_FAILED_TO_INITIALIZE, TOOL_NAME


@click.pass_context
def needs_settings(ctx: click.Context, autofix: bool=False):
    """
    Loads and verifies settings.
    If settings are missing, tries to fix them.
    Performs sys.exit on error.
    Meant to be used as first line in click commands that needs settings to be correct.
    """
    settings_path: Path = ctx.obj['settings_path']

    logging.info(f"Loading settings at {settings_path}")
    try:
        settings.load_and_verify_settings(settings_path)
    except settings.SettingsException as e:
        if autofix:
            print("Things are not set up correctly. Give me some time to fix that now...", file=sys.stderr)
            logging.info(f"Could not load settings successfully ({str(e)}); attempting to fix it")
            setup.initialize(settings_path)
            print("I believe I have been able to configure everything correctly", file=sys.stderr)
            try:
                settings.load_and_verify_settings(settings_path)
            except settings.InvalidRepositoryRoot as e:
                logging.critical("\n".join([
                    f"Your settings claim that your repo is located in {e.path}",
                    f"but that doesn't seem to be the case...",
                    f"If you moved your repository, you can tell progtool",
                    f"about its new location using progtool relocate",
                    f"{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/relocating.html",
                    f"Otherwise, you can also try to go for a manual setup, as described here",
                    f"{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/manual-setup.html"
                ]))
                sys.exit(ERROR_CODE_FAILED_TO_INITIALIZE)
            except settings.SettingsException as e:
                logging.critical("\n".join([
                    'It looks like I failed :-(',
                    "I'm afraid you'll have to set things up manually",
                    f"Error message: {str(e)}",
                    f"{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/manual-setup.html"
                ]))
                sys.exit(ERROR_CODE_FAILED_TO_INITIALIZE)
        else:
            logging.critical("\n".join([
                "Failed to load settings",
                f"You can try to fix them using {TOOL_NAME} settings fix",
            ]))
            sys.exit(ERROR_CODE_FAILED_TO_INITIALIZE)


def is_indexed(string: str) -> bool:
    """
    Checks if string starts with a index prefix.
    """
    return bool(re.fullmatch(r'\d+(-.+)?', string))


def is_indexed_directory(path: str) -> bool:
    """
    Checks if path refers to a directory and its name is indexed.
    """
    return is_indexed(path) and os.path.isdir(path)


def remove_index_from_string(string: str) -> str:
    """
    Removes the number prefix from the string.
    """
    return extract_index_and_name(string)[1]


def remove_index_from_path(path: Path) -> Path:
    """
    Removes the number prefix from the path.
    """
    return Path(remove_index_from_string(str(path)))


def extract_index_and_name(string: str) -> tuple[int, str]:
    if match := re.fullmatch(r'(\d+)', string):
        index = int(match.group(1))
        filename = ''
    elif match := re.fullmatch(r'(\d+)-(.*)', string):
        index = int(match.group(1))
        filename = match.group(2)

    return (index, filename)


def index_of(path: str | Path) -> int:
    if isinstance(path, Path):
        string = str(path)
    else:
        string = path

    return extract_index_and_name(string)[0]


def add_index_to_string(string: str, index: int) -> str:
    index_string = str(index).rjust(2, '0')

    if len(string) == 0:
        return index_string
    else:
        return f'{index_string}-{string}'


def add_index_to_path(path: Path, index: int) -> Path:
    return Path(add_index_to_string(str(path), index))


def find_indexed_subdirectories(path: Optional[Path] = None) -> list[Path]:
    return [Path(entry) for entry in os.listdir(path) if is_indexed_directory(entry)]


def replace_index_in_path(path: Path, new_index: int) -> Path:
    without_index = remove_index_from_path(path)
    return add_index_to_path(without_index, new_index)


def create_reindexing_mapping(paths: list[Path]) -> dict[Path, Path]:
    sorted_paths = sorted(paths)
    indexed_paths = {
        path: add_index_to_path(remove_index_from_path(path), index)
        for index, path in zip(count(start=1), sorted_paths)
    }
    return indexed_paths


def find_lowest_unused_index_in_strings(strings: list[str]) -> int:
    '''
    Returns the lowest unused index which is higher than all indices in use.
    In other words, this function does not look for gaps in the indexing.
    '''
    indices = [extract_index_and_name(string)[0] for string in strings]
    highest_index = max(indices)
    return highest_index + 1


def find_lowest_unused_index_in_directory(path: Optional[Path] = None) -> int:
    indexed_subdirectories = find_indexed_subdirectories(path)
    indexed_subdirectories_names = [str(subdir) for subdir in indexed_subdirectories]
    return find_lowest_unused_index_in_strings(indexed_subdirectories_names)


def make_slug(string: str) -> str:
    return '-'.join(string.lower().split(' '))
