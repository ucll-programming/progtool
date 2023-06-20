import click
import os
from progtool.cli import util
from pathlib import Path
import yaml

from progtool.material.metadata import SectionMetadata, TYPE_SECTION


@click.group()
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
