import click
import progtool.server


@click.command(help='Set up server')
def server():
    progtool.server.run()