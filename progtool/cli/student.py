import click
import git
import logging
import progtool.constants as constants
import sys
from pathlib import Path

from progtool.repository import IdentifierFileException, InvalidIdentifierFile, MissingIdentifierFile, NoGitRepository, check_repository_identifier, find_course_material_repository, find_repository, root_of_repository



def is_student(actor: git.Actor) -> bool:
    if not actor.email:
        return False
    return 'student' in actor.email and actor.name != 'Brecht Van Eylen'


@click.group()
@click.pass_context
def student(ctx: click.Context) -> None:
    """
    Student related functionality
    """
    pass


@student.command()
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
def verify(path: str):
    """
    Performs a few checks on the student repository
    """
    logging.info(f'Looking for repository in {str}')
    try:
        repository = find_repository(Path(path))
    except NoGitRepository:
        print(f'{path} does not refer to a Git repository')
        sys.exit(constants.ERROR_CODE_GITHUB_ORGANIZATION_NOT_FOUND)
    logging.info('Repository found')
    logging.info("Looking for repository's root")
    root = root_of_repository(repository)
    logging.info(f'Repository root is {root}')
    logging.info('Checking identifier')
    try:
        check_repository_identifier(root)
    except MissingIdentifierFile:
        print('Repository does not seem to contain course material')
        sys.exit(constants.ERROR_CODE_MISSING_IDENTIFIER_FILE)
    except InvalidIdentifierFile:
        print('Course material identifier corrupted')
        sys.exit(constants.ERROR_CODE_WRONG_IDENTIFIER_CONTENTS)

    logging.info('Checking active branch')
    active_branch = repository.active_branch.name
    if active_branch != 'master':
        print(f'Active branch should be master, but it is {active_branch} instead')
        sys.exit(constants.ERROR_CODE_WRONG_ACTIVE_BRANCH)

    print('Everything seems okay')
    sys.exit(0)


@student.command(name="count-commits")
@click.argument("path", type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
def count_commits(path: str):
    """
    Count commits made by student
    """
    logging.info(f'Looking for git repository at {path}')
    try:
        repository = find_course_material_repository(Path(path))
    except NoGitRepository:
        logging.critical(f"No repository found at {path}; I have even looked in parent directories")
        sys.exit(constants.ERROR_CODE_NO_GIT_REPOSITORY)

    logging.info(f'Found repository')

    logging.info('Iterating through commits')
    count = 0
    for commit in repository.iter_commits('master'):
        author = commit.author
        if author and is_student(author):
            count += 1
    print(count)
