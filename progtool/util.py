from pathlib import Path
import contextlib
import os


@contextlib.contextmanager
def in_directory(path: Path):
    current_directory = path.cwd()
    os.chdir(path)
    yield
    os.chdir(current_directory)
