from enum import Enum, auto
from pathlib import Path

import logging
from progtool import constants
from progtool.constants import *
import git
import sys


def find_repository_root(directory: Path) -> Path:
    logging.info(f'Looking for git repository root starting in {directory}')
    try:
        repo = git.Repo(str(directory), search_parent_directories=True)
    except:
        logging.info(f'No Git repo found at {directory}')
        raise NoGitRepository(directory)

    logging.debug('Found a repository; getting root directory')
    root = Path(repo.git.rev_parse("--show-toplevel")).absolute()
    logging.debug(f'Determined that root directory is {root}')

    # Raises exception if anything went wrong
    check_repository_identifier(root)

    logging.info(f'Valid repository root directory has been found at {root}')
    return root


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

    logging.debug(f'Looking for identifier file {identifier_file_path}')
    if not identifier_file_path.is_file():
        logging.debug(f'Could not find {identifier_file_path}')
        raise MissingIdentifierFile()
    logging.debug(f'Found identifier file!')


def check_contents_of_repository_identifier(identifier_file_path: Path) -> None:
    logging.debug(f'Checking contents of identifier file')
    contents = identifier_file_path.read_text()
    if contents != IDENTIFIER_FILE_CONTENTS:
        logging.debug(f'File {identifier_file_path} contains invalid data')
        raise InvalidIdentifierFile()
    logging.debug(f'Identifier file has right contents!')
