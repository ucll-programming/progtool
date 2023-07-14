from pathlib import Path

from progtool import settings


def find_repository_root() -> Path:
    # repo = git.Repo('.', search_parent_directories=True)
    # root = repo.working_tree_dir
    # return Path(root).resolve()

    # TODO
    return settings.repository_root()


def find_exercises_root() -> Path:
    return find_repository_root() / 'exercises'
