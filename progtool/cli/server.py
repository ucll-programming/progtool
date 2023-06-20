import click


@click.command(help='Set up server')
def server():
    import progtool.server
    progtool.server.run()