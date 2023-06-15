import argparse
import logging
from progtool.cli import server



def process_command_line_arguments():
    root_parser = argparse.ArgumentParser(description='Programming Assistant Tool')
    root_parser.add_argument('-v', '--verbose', action='count', dest='verbosity')
    subparsers = root_parser.add_subparsers()

    server.add_command_line_parser(subparsers)
    args = root_parser.parse_args()

    _set_verbosity_level(args.verbosity)

    if 'func' in args:
        args.func()
    else:
        _show_help()


def _show_help():
    # print('Help!')
    from progtool.material.tree import create_material_tree
    from progtool.repository import find_exercises_root
    tree = create_material_tree(find_exercises_root())
    print(tree.children)


def _set_verbosity_level(level):
    match level:
        case 1:
            logging.basicConfig(level=logging.INFO, force=True)
            logging.info('Verbosity set to INFO level')
        case 2:
            logging.basicConfig(level=logging.DEBUG, force=True)
            logging.debug('Verbosity set to DEBUG level')
