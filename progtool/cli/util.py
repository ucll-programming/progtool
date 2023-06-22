from itertools import count
import os
import re


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


def remove_index(string: str) -> str:
    """
    Removes the number prefix from the string.
    """
    return extract_index_and_name(string)[1]


def extract_index_and_name(string: str) -> tuple[int, str]:
    if match := re.fullmatch(r'(\d+)', string):
        index = int(match.group(1))
        filename = ''
    elif match := re.fullmatch(r'(\d+)-(.*)', string):
        index = int(match.group(1))
        filename = match.group(2)

    return (index, filename)


def add_index(string: str, number: int) -> str:
    index_string = str(number).rjust(2, '0')

    if len(string) == 0:
        return index_string
    else:
        return f'{index_string}-{string}'


def find_indexed_subdirectories() -> list[str]:
    return [entry for entry in os.listdir() if is_indexed_directory(entry)]


def create_reindexing_mapping(strings: list[str]) -> dict[str, str]:
    sorted_strings = sorted(strings)
    indexed_string = {
        string: add_index(remove_index(string), index)
        for index, string in zip(count(start=1), sorted_strings)
    }
    return indexed_string


def find_lowest_unused_index(strings: list[str]) -> int:
    '''
    Returns the lowest unused index which is higher than all indices in use.
    In other words, this function does not look for gaps in the indexing.
    '''
    indices = [extract_index_and_name(string)[0] for string in strings]
    highest_index = max(indices)
    return highest_index + 1


def make_slug(string: str) -> str:
    return '-'.join(string.lower().split(' '))
