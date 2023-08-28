from enum import Enum, auto
from pathlib import Path

import logging
from progtool.constants import *
import git
import sys


def find_repository_root(directory: Path) -> Path:
    logging.info('Looking for git repository root starting in {directory}')
    repo = git.Repo(str(directory), search_parent_directories=True)

    logging.debug('Found a repository; getting root directory')
    root = Path(repo.git.rev_parse("--show-toplevel")).absolute()
    logging.debug(f'Determined that root directory is {root}')

    result = check_repository_identifier(root)
    if result == RepositoryIdentifierResult.MISSING_FILE:
        logging.critical("\n".join([
            f'Could not find identifier file {IDENTIFIER_FILE}',
            f"This either means you have removed it or that you're running this script in the wrong repository",
            f"Make sure to run it inside the course material repository",
            f"{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/missing-identifier-file.html"
        ]))
        sys.exit(ERROR_CODE_MISSING_IDENTIFIER_FILE)
    elif result == RepositoryIdentifierResult.WRONG_CONTENTS:
        logging.critical("\n".join([
            f"The identifier file has the wrong contents",
            f"This is very surprising and really shouldn't happen."
            f"{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/wrong-identifier-file-contents.html"
        ]))
        sys.exit(ERROR_CODE_WRONG_IDENTIFIER_CONTENTS)

    logging.info(f'Repository root directory has been found at {root}')
    return root


class RepositoryIdentifierResult(Enum):
    SUCCESS = auto()
    MISSING_FILE = auto()
    WRONG_CONTENTS = auto()


def check_repository_identifier(directory: Path) -> RepositoryIdentifierResult:
    logging.info('Looking for repository identifier')
    identifier_file_path = directory / IDENTIFIER_FILE
    logging.debug(f'Looking for identifier file {identifier_file_path}')
    if not identifier_file_path.is_file():
        logging.debug(f'Could not find {identifier_file_path}')
        return RepositoryIdentifierResult.MISSING_FILE
    logging.debug(f'Found identifier file!')

    logging.debug(f'Checking contents of identifier file')
    contents = identifier_file_path.read_text()
    if contents != IDENTIFIER_FILE_CONTENTS:
        logging.debug(f'File {identifier_file_path} contains invalid data')
        return RepositoryIdentifierResult.WRONG_CONTENTS
    logging.debug(f'Identifier file has right contents!')

    return RepositoryIdentifierResult.SUCCESS
