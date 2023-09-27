from enum import Enum, auto
from pathlib import Path

import logging
from progtool import constants
from progtool.constants import *
import git


def find_repository(directory: Path) -> git.Repo:
    logging.info(f'Looking for git repository root starting in {directory}')
    try:
        return git.Repo(str(directory), search_parent_directories=True)
    except:
        logging.error(f'No Git repo found at {directory}')
        raise NoGitRepository(directory)


def find_course_material_repository(directory: Path) -> git.Repo:
    logging.info(f"Looking for course material repository at {directory}")
    repository = find_repository(directory)
    root = root_of_repository(repository)

    # Raises exception if anything went wrong
    check_repository_identifier(root)

    return repository


def root_of_repository(repository: git.Repo) -> Path:
    return Path(repository.git.rev_parse("--show-toplevel")).absolute()


def find_course_material_repository_root(directory: Path) -> Path:
    repo = find_course_material_repository(directory)
    return root_of_repository(repo)


class RepositoryException(Exception):
    pass

class NoGitRepository(RepositoryException):
    def __init__(self, path: Path):
        super().__init__(f'No Git repository found at {path}')

class IdentifierFileException(RepositoryException):
    pass

class MissingIdentifierFile(IdentifierFileException):
    def __init__(self):
        super().__init__(f'Identifier file {constants.IDENTIFIER_FILE} missing')

class InvalidIdentifierFile(IdentifierFileException):
    def __init__(self):
        super().__init__(f'Identifier file has invalid contents')


def check_repository_identifier(directory: Path) -> None:
    identifier_file_path = directory / IDENTIFIER_FILE
    check_existence_of_repository_identifier(identifier_file_path)
    check_contents_of_repository_identifier(identifier_file_path)


def check_existence_of_repository_identifier(identifier_file_path: Path) -> None:
    logging.info('Checking repository identifier')

    logging.info(f'Looking for identifier file {identifier_file_path}')
    if not identifier_file_path.is_file():
        logging.info(f'Could not find {identifier_file_path}')
        raise MissingIdentifierFile()
    logging.info(f'Found identifier file!')


def check_contents_of_repository_identifier(identifier_file_path: Path) -> None:
    logging.info(f'Checking contents of identifier file')
    contents = identifier_file_path.read_text()
    if contents != IDENTIFIER_FILE_CONTENTS:
        logging.info(f'File {identifier_file_path} contains invalid data')
        raise InvalidIdentifierFile()
    logging.info(f'Identifier file has right contents!')
