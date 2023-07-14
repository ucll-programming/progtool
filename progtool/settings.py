import os
from pathlib import Path


def language_priorities():
    return ['en', 'nl']


def html_path():
    computer_name = os.environ['COMPUTERNAME']

    if computer_name == 'LT2180298':
        return 'C:/repos/ucll/programming/frontend/dist/index.html'
    else:
        return 'G:/repos/ucll/programming/frontend/dist/index.html'


def repository_root() -> Path:
    computer_name = os.environ['COMPUTERNAME']

    if computer_name == 'LT2180298':
        return Path('C:/repos/ucll/programming/course-material')
    else:
        return Path('G:/repos/ucll/programming/course-material')
