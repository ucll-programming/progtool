from typing import cast
from progtool.material.metadata import load_metadata
from progtool.material.tree import Exercise, Section, Explanation, build_tree
from progtool.repository import find_exercises_root
import click


@click.command()
def check() -> None:
    print('Checking!')
