import click
from progtool import log
from progtool.cli.tree import tree
from progtool.cli.server import server
from progtool.cli.renumber import renumber
from progtool.cli.create import create


@click.group()
@click.option('-v', '--verbose', count=True)
def cli(verbose):
    log.configure(verbose)


@cli.command()
def test():
    from progtool import repository
    from progtool.material.tree import create_material_tree
    import asyncio

    async def wait():
        root.judge_recursively()
        await asyncio.sleep(2)

    root = create_material_tree(repository.find_exercises_root())
    asyncio.run(wait())


def process_command_line_arguments():
    commands = [
        tree,
        server,
        renumber,
        create,
    ]

    for command in commands:
        cli.add_command(command)

    cli()
