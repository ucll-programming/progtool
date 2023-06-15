import argparse
from progtool.cli import server


def process_command_line_arguments():
    root_parser = argparse.ArgumentParser(description='Programming Assistant Tool')
    subparsers = root_parser.add_subparsers()

    server.add_command_line_parser(subparsers)
    args = root_parser.parse_args()

    if 'func' in args:
        args.func()
    else:
        _show_help()


def _show_help():
    print('Help!')
