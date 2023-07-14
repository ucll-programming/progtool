from pathlib import Path


def find_repository_root() -> Path:
    # repo = git.Repo('.', search_parent_directories=True)
    # root = repo.working_tree_dir
    # return Path(root).resolve()

    # TODO
    import os
    computer_name = os.environ['COMPUTERNAME']

    if computer_name == 'LT2180298':
        return Path('C:/repos/ucll/programming/course-material')
    else:
        return Path('G:/repos/ucll/programming/course-material')


def find_exercises_root() -> Path:
    return find_repository_root() / 'exercises'
