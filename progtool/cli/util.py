from pathlib import Path
from typing import Optional
from itertools import count
import os
import re
import contextlib



@contextlib.contextmanager
def in_directory(path: Path):
    current_directory = path.cwd()
    os.chdir(path)
    yield
    os.chdir(current_directory)


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
