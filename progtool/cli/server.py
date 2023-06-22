import click


@click.command()
def server():
    """
    Set up server.
    """
    import progtool.server
    progtool.server.run()