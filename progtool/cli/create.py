import click
import os
from progtool.cli import util
from pathlib import Path
import yaml

from progtool.material.metadata import SectionMetadata, TYPE_SECTION, TYPE_EXERCISE


@click.group(help="Helps with the creation of new material")
def create():
    pass


@create.command(help='Create new section')
@click.argument("name", type=str)
def section(name):
    number = util.find_lowest_unused_number(util.find_numbered_subdirectories())
    slug = util.make_slug(name)
    dirname = Path(util.add_number(slug, number))
    os.mkdir(dirname)
    with open(dirname / 'metadata.yaml', 'w') as file:
        metadata = SectionMetadata(name=name, type=TYPE_SECTION)
        yaml.dump(metadata.dict(), file, default_flow_style=False)


@create.command(help='Create new exercise')
@click.argument("name", type=str)
def exercise(name):
    number = util.find_lowest_unused_number(util.find_numbered_subdirectories())
    slug = util.make_slug(name)
    dirname = Path(util.add_number(slug, number))
    os.mkdir(dirname)
    with open(dirname / 'metadata.yaml', 'w') as file:
        metadata = SectionMetadata(name=name, type=TYPE_EXERCISE)
        yaml.dump(metadata.dict(), file, default_flow_style=False)
    with open(dirname / 'assignment.md', 'w') as file:
        file.write(f'# {name}\n\nTODO')
    with open(dirname / 'solution.py', 'w') as file:
        file.write('TODO')
    with open(dirname / 'tests.py', 'w') as file:
        file.write('import pytest\n\nTODO')
