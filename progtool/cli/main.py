import click
from progtool import log
from progtool.cli.tree import tree
from progtool.cli.server import server
from progtool.cli.create import create
from progtool.cli.index import index
from progtool.cli.check import check


@click.group()
@click.option('-v', '--verbose', count=True)
def cli(verbose):
    log.configure(verbose)


def process_command_line_arguments():
    commands = [
        tree,
        server,
        index,
        create,
        check,
    ]

    for command in commands:
        cli.add_command(command)

    cli()
