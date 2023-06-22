import click
import os
from progtool.cli import util
from pathlib import Path
import yaml

from progtool.material.metadata import SectionMetadata, TYPE_SECTION, TYPE_EXERCISE


@click.group(help="Helps with the creation of new material")
@click.option('-x', '--unindexed', help="don't add number prefix", is_flag=True, default=False)
@click.pass_context
def create(ctx, unindexed):
    ctx.ensure_object(dict)
    ctx.obj['unindexed'] = unindexed


@create.command(help='Create new section')
@click.argument("name", type=str)
@click.pass_context
def section(ctx, name):
    unindexed = ctx.obj['unindexed']
    slug = util.make_slug(name)
    dirname = add_index(string=slug, unindexed=unindexed)

    os.mkdir(dirname)
    with open(dirname / 'metadata.yaml', 'w') as file:
        metadata = SectionMetadata(name=name, type=TYPE_SECTION)
        yaml.dump(metadata.dict(), file, default_flow_style=False)


@create.command(help='Create new exercise')
@click.argument("name", type=str)
@click.pass_context
def exercise(ctx, name):
    unindexed = ctx.obj['unindexed']
    slug = util.make_slug(name)
    dirname = add_index(string=slug, unindexed=unindexed)

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


def add_index(*, string: str, unindexed: bool) -> Path:
    if unindexed:
        dirname = Path(string)
    else:
        number = util.find_lowest_unused_index_in_directory()
        dirname = Path(util.add_index_to_string(string, number))
    return dirname
