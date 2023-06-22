import click
import os
from progtool.cli import util
from pathlib import Path
import yaml

from progtool.material.metadata import SectionMetadata, TYPE_SECTION, TYPE_EXERCISE


@click.group(help="Helps with the creation of new material")
@click.option('-x', '--unnumbered', help="don't add number prefix", is_flag=True, default=False)
@click.pass_context
def create(ctx, unnumbered):
    ctx.ensure_object(dict)
    ctx.obj['unnumbered'] = unnumbered


@create.command(help='Create new section')
@click.argument("name", type=str)
@click.pass_context
def section(ctx, name):
    unnumbered = ctx.obj['unnumbered']
    slug = util.make_slug(name)
    dirname = add_number_prefix(string=slug, unnumbered=unnumbered)

    os.mkdir(dirname)
    with open(dirname / 'metadata.yaml', 'w') as file:
        metadata = SectionMetadata(name=name, type=TYPE_SECTION)
        yaml.dump(metadata.dict(), file, default_flow_style=False)


@create.command(help='Create new exercise')
@click.argument("name", type=str)
@click.pass_context
def exercise(ctx, name):
    unnumbered = ctx.obj['unnumbered']
    slug = util.make_slug(name)
    dirname = add_number_prefix(string=slug, unnumbered=unnumbered)

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


def add_number_prefix(*, string: str, unnumbered: bool) -> Path:
    if unnumbered:
        dirname = Path(string)
    else:
        number = util.find_lowest_unused_number(util.find_numbered_subdirectories())
        dirname = Path(util.add_number(string, number))
    return dirname
