from itertools import count
import os
import re


def is_numbered(string: str) -> bool:
    """
    Checks if string starts with a number prefix.
    """
    return bool(re.fullmatch(r'\d+(-.+)?', string))


def is_numbered_directory(path: str) -> bool:
    """
    Checks if path refers to a directory and its name is numbered.
    """
    return is_numbered(path) and os.path.isdir(path)


def remove_number(string: str) -> str:
    """
    Removes the number prefix from the string.
    """
    return extract_number_and_name(string)[1]


def extract_number_and_name(string: str) -> tuple[int, str]:
    if match := re.fullmatch(r'(\d+)', string):
        number = int(match.group(1))
        filename = ''
    elif match := re.fullmatch(r'(\d+)-(.*)', string):
        number = int(match.group(1))
        filename = match.group(2)

    return (number, filename)


def add_number(string: str, number: int) -> str:
    number_string = str(number).rjust(2, '0')

    if len(string) == 0:
        return number_string
    else:
        return f'{number_string}-{string}'


def find_numbered_subdirectories() -> list[str]:
    return [entry for entry in os.listdir() if is_numbered_directory(entry)]


def create_renumbering_mapping(strings: list[str]) -> dict[str, str]:
    sorted_strings = sorted(strings)
    renumbered_strings = {
        string: add_number(remove_number(string), index)
        for index, string in zip(count(start=1), sorted_strings)
    }
    return renumbered_strings


def find_lowest_unused_number(strings: list[str]) -> int:
    '''
    Returns the lowest unused number which is higher than all numbers in use.
    In other words, this function does not look for gaps in the numbering.
    '''
    numbers = [extract_number_and_name(string)[0] for string in strings]
    highest_number = max(numbers)
    return highest_number + 1


def make_slug(string: str) -> str:
    return '-'.join(string.lower().split(' '))
