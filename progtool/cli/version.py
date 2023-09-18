import click


@click.command()
def version() -> None:
    """
    Prints out version
    """
    import pkg_resources
    v = pkg_resources.get_distribution('progtool').version
    print(v)
