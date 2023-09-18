import logging
import os
import sys
from pathlib import Path
from typing import cast

import click

import progtool.settings as settings
from progtool import constants
from progtool.repository import InvalidIdentifierFile, MissingIdentifierFile, find_repository_root


@click.command()
@click.pass_context
def relocate(ctx):
    """
    Informs progtool about a relation
    """
    logging.info("Loading settings")
    settings_path: Path = cast(Path, ctx.obj['settings_path'])
    s = settings.load_settings(settings_path)

    current_path = Path(os.getcwd())
    logging.debug(f"Current path: {current_path}")

    try:
        logging.debug("Looking for repository root")
        s.repository_root = find_repository_root(current_path)
        logging.debug(f"Repository root found at {s.repository_root}")
        logging.debug(f"Overwriting setting file at {settings_path}")
        settings.write_settings_file(settings=s, path=settings_path)
        print(f"Relocated to {s.repository_root}")
    except MissingIdentifierFile:
        logging.critical("\n".join([
            "No identifier file found",
            "You do not seem to be located somewhere inside the course material repository"
        ]))
        sys.exit(constants.ERROR_CODE_MISSING_IDENTIFIER_FILE)
    except InvalidIdentifierFile:
        logging.critical("\n".join([
            "Identifier file found, but with wrong contents"
        ]))
        sys.exit(constants.ERROR_CODE_WRONG_IDENTIFIER_CONTENTS)
