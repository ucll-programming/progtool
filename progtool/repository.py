from pathlib import Path
import git


def find_repository_root() -> Path:
    # repo = git.Repo('.', search_parent_directories=True)
    # root = repo.working_tree_dir
    # return Path(root).resolve()
    return Path('G:/repos/ucll/programming/course-material')


def find_exercises_root() -> Path:
    return find_repository_root() / 'exercises'
