import logging
import sys
from pathlib import Path
import click

from progtool import settings
from progtool.cli import setup
from progtool.constants import ERROR_CODE_FAILED_TO_INITIALIZE


def load_settings(context: click.Context):
    settings_path: Path = Path(context.params['settings_path_string'])

    logging.info(f"Loading settings at {settings_path}")
    try:
        settings.load_and_verify_settings(settings_path)
    except settings.SettingsException as e:
        print("Things are not set up correctly. Give me some time to fix that now...", file=sys.stderr)
        logging.info(f"Could not load settings successfully ({str(e)}); attempting to fix it")
        setup.initialize(settings_path)
        print("I believe I have been able to configure everything correctly", file=sys.stderr)
        try:
            settings.load_and_verify_settings(settings_path)
        except settings.SettingsException as e:
            logging.critical("\n".join([
                'It looks like I failed :-(',
                "I'm afraid you'll have to set things up manually",
                f"Error message: {str(e)}",
                "f'{COURSE_MATERIAL_DOCUMENTATION_URL}/troubleshooting/manual-setup.html'"
            ]))
            sys.exit(ERROR_CODE_FAILED_TO_INITIALIZE)
