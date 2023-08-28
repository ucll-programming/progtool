import os
from pathlib import Path

import click
import yaml

from progtool.cli import util
from progtool.content.metadata import (TYPE_EXERCISE, TYPE_SECTION,
                                       ExerciseMetadata, SectionMetadata)


@click.group(help="Helps with the creation of new content")
@click.option('-x', '--unindexed', help="don't add number prefix", is_flag=True, default=False)
@click.pass_context
def create(ctx, unindexed):
    ctx.ensure_object(dict)
    ctx.obj['unindexed'] = unindexed

