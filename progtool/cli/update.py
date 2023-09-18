import click
import sys


@click.command()
def update() -> None:
    """
    Shows how to update progtool
    """
    print("Write the following command:")
    print("  pipx upgrade progtool")