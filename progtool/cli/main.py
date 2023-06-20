import argparse
from progtool import log
from progtool.cli import server, tree, renumber


def process_command_line_arguments():


    root_parser = argparse.ArgumentParser(description='Programming Assistant Tool')
    root_parser.add_argument('-v', '--verbose', action='count', dest='verbosity', help='Increase verbosity level')
    subparsers = root_parser.add_subparsers()

    command_modules = [
        server,
        tree,
        renumber
    ]

    for module in command_modules:
        module.add_command_line_parser(subparsers)

    args = root_parser.parse_args()
    log.configure(args.verbosity)

    if 'func' in args:
        args.func(args)
    else:
        _show_help()


def _show_help():
    print('Help!')
